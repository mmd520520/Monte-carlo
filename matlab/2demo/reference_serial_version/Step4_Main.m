function results = Step4_Main(photonCount, smokeTest, seed, saveResults)
    % 第4步主函数。依次调用第1～3步，再发射光子并循环调用第5～9步。
    % results=Step4_Main(2000,false,1,true);
    % photonCount光子数；smokeTest粗网格；seed随机种子；saveResults是否保存。
    if nargin < 1
        photonCount = [];
    end
    if nargin < 2
        smokeTest = false;
    end
    if nargin < 3
        seed = 1;
    end
    if nargin < 4
        saveResults = true;
    end
    [model, tissue, config, tallies] = Prepare_Inputs(photonCount, smokeTest, seed);
    rng(config.seed, 'twister');
    timer = tic;
    for iphoton = 1:config.Nphotons
        photon = Step4_Launch(config.source, model);
        tallies.Nlaunched = tallies.Nlaunched+1;
        while photon.alive
            [photon, deposits, event, nBoundary] = Step5_Hop(photon, model, tissue);
            % 索引可能重复，因此逐项累加，不能使用重复索引的向量赋值。
            for k = 1:numel(deposits.indices)
                j = deposits.indices(k);
                tallies.Araw(j) = tallies.Araw(j)+deposits.weights(k);
            end
            tallies.boundaryEvents = tallies.boundaryEvents+nBoundary;
            switch event.kind
                case 'top'
                    tallies.Rraw(event.surfaceIndex) = tallies.Rraw(event.surfaceIndex)+event.weight;
                case 'bottom'
                    tallies.Traw(event.surfaceIndex) = tallies.Traw(event.surfaceIndex)+event.weight;
                case 'side'
                    tallies.sideEscapeRaw = tallies.sideEscapeRaw+event.weight;
            end
            if ~isempty(event.airIndices)
                tallies.airEscapedPackets = tallies.airEscapedPackets+1;
                for k = 1:numel(event.airIndices)
                    j = event.airIndices(k);
                    tallies.AirPathRaw(j) = tallies.AirPathRaw(j)+event.airWeights(k);
                end
            end
            if photon.alive
                [photon, correction] = Step8_SpinCheck(photon, tissue, config.roulette);
                tallies.scatteringEvents = tallies.scatteringEvents+1;
                tallies.rouletteBalanceRaw = tallies.rouletteBalanceRaw+correction;
            end
        end
        tallies.Nterminated = tallies.Nterminated+1;
        if mod(iphoton, max(1, floor(config.Nphotons/10))) == 0
            fprintf('%d / %d photons\n', iphoton, config.Nphotons);
        end
    end
    results = Step9_Output(tallies, model, tissue, config);
    results.elapsedSeconds = toc(timer);
    results.smokeTest = smokeTest;
    fprintf('Energy sum = %.10f; with roulette correction = %.10f\n', ...
        results.energyTotal, results.bookkeepingTotal);
    fprintf('Elapsed: %.2f seconds\n', results.elapsedSeconds);
    if saveResults
        if smokeTest
            name = 'mc_smoke_results.mat';
        else
            name = 'mc_results.mat';
        end
        save(fullfile(fileparts(mfilename('fullpath')), name), 'results', '-v7.3');
    end
end
