function report = Test_ParallelOblique(runParallel)
    % 小网格测试；runParallel=true时实际启动/使用2个进程进行一致性核验。
    if nargin < 1
        runParallel = true;
    end
    [model, tissue, config, ~] = Prepare_Inputs(121, true, 7);
    source = config.source;
    [normal, r0] = Configure_ObliqueSource(source, tissue, 0, 0);
    expected = ((tissue(1).n - tissue(5).n) / (tissue(1).n + tissue(5).n))^2;
    assert(abs(r0 - expected) < 1e-14);
    assert(norm(normal.uAir - [0, 0, 1]) < 1e-14);

    [config.source, config.Rsp] = Configure_ObliqueSource(source, tissue, 30, 0);
    transmitted = [config.source.ux, config.source.uy, config.source.uz];
    assert(abs(norm(transmitted) - 1) < 1e-14);
    assert(abs(tissue(1).n * sind(30) - ...
        tissue(5).n * sind(config.source.thetaTissueDeg)) < 1e-14);
    assert(config.source.W0 > 0 && config.source.W0 < 1);

    % 检查空气中的入射光柱向左上方延伸，而反射方向向右上方。
    fake.Phi = zeros(model.size);
    fake.source = config.source;
    fake.x = model.x;
    fake.z = model.z;
    fake.dy = model.dy;
    fake.specular = 0;
    fake = AddIncidentAirBeam(fake);
    xCenter = model.x - model.dx / 2;
    slice = fake.Phi(:, :, 1);
    rowWeights = sum(slice, 2);
    centroid = sum(xCenter .* rowWeights) / sum(rowWeights);
    expectedX = -(model.zsurf - model.dz / 2) * tand(30);
    assert(abs(centroid - expectedX) < model.dx);
    rebuilt = AddIncidentAirBeam(fake);
    assert(isequaln(fake.Phi, rebuilt.Phi));

    settings = MC_Settings(struct('useParallel', false, 'numWorkers', 2, ...
        'batchSize', 40, 'thetaDeg', 30));
    config.options = settings;
    initial = MC_CreateTallies(model);
    [serial, ~, batches] = MC_RunBatches(model, tissue, config, initial, settings);
    assert(batches == 4 && serial.Nlaunched == 121);
    [serialAgain, ~, ~] = MC_RunBatches(model, tissue, config, initial, settings);
    assert(isequal(serial.Araw, serialAgain.Araw));
    result = Step9_Output(serial, model, tissue, config);
    assert(abs(result.bookkeepingTotal - 1) < 1e-8);
    assert(result.airEscapedPackets > 0);

    if runParallel
        previousPool = gcp('nocreate');
        testOwnsPool = isempty(previousPool);
        cleanupPool = onCleanup(@() Cleanup_TestPool(testOwnsPool));
        settings.useParallel = true;
        [parallel, workers, ~] = MC_RunBatches(model, tissue, config, initial, settings);
        assert(workers == 2);
        assert(isequal(serial.Araw, parallel.Araw));
        assert(isequal(serial.Rraw, parallel.Rraw));
        assert(isequal(serial.AirPathRaw, parallel.AirPathRaw));
        assert(serial.Nterminated == parallel.Nterminated);
        assert(serial.rouletteBalanceRaw == parallel.rouletteBalanceRaw);
        clear cleanupPool;
    end

    report = struct('fresnel', true, 'snell', true, 'airBeamGeometry', true, ...
        'idempotence', true, 'reproducibility', true, 'energy', true, ...
        'parallelTested', runParallel);
    disp(report);
    disp('PARALLEL_OBLIQUE_TESTS_PASSED');
end

function Cleanup_TestPool(testOwnsPool)
    % 只关闭本测试新建的池，不关闭用户已有的池。
    if testOwnsPool
        pool = gcp('nocreate');
        if ~isempty(pool)
            delete(pool);
        end
    end
end
