function [total, workersUsed, batchCount] = MC_RunBatches(model, tissue, config, total, options)
    % 固定分批与合并顺序，串行/并行结果可复现。
    batchCount = ceil(config.Nphotons / options.batchSize);
    counts = repmat(options.batchSize, 1, batchCount);
    counts(end) = config.Nphotons - options.batchSize * (batchCount - 1);
    completedPhotons = 0;
    if ~options.useParallel
        workersUsed = 1;
        for batchID = 1:batchCount
            packet = MC_RunBatch(model, tissue, config, counts(batchID), batchID);
            total = MC_MergeTallies(total, packet);
            completedPhotons = completedPhotons + counts(batchID);
            fprintf('Serial: %d / %d photons; batch %d / %d\n', ...
                completedPhotons, config.Nphotons, batchID, batchCount);
        end
        return;
    end
    assert(license('test', 'Distrib_Computing_Toolbox'), ...
        '并行运行需要Parallel Computing Toolbox；也可设置useParallel=false。');
    pool = gcp('nocreate');
    if isempty(pool)
        pool = parpool('local', options.numWorkers);
    end
    assert(isa(pool, 'parallel.ProcessPool'), '请使用local/Processes进程池。');
    workersUsed = min([options.numWorkers, pool.NumWorkers, batchCount]);
    fprintf('Pool workers %d; requested maximum %d; active batches %d\n', ...
        pool.NumWorkers, options.numWorkers, workersUsed);
    codeDir = fileparts(mfilename('fullpath'));
    codeFiles = dir(fullfile(codeDir, '*.m'));
    attached = fullfile({codeFiles.folder}, {codeFiles.name});
    addAttachedFiles(pool, attached);
    updateAttachedFiles(pool);
    modelConstant = parallel.pool.Constant(model);
    releaseModel = onCleanup(@() delete(modelConstant));
    futures = cell(1, workersUsed);
    try
        for batchID = 1:workersUsed
            futures{batchID} = parfeval(pool, @MC_RunBatch, 1, ...
                modelConstant, tissue, config, counts(batchID), batchID);
        end
        % 滚动提交，只保留有限个任务；按编号获取使合并顺序确定。
        for batchID = 1:batchCount
            slot = mod(batchID - 1, workersUsed) + 1;
            packet = fetchOutputs(futures{slot});
            futures{slot} = [];
            total = MC_MergeTallies(total, packet);
            clear packet;
            completedPhotons = completedPhotons + counts(batchID);
            fprintf('Parallel (%d active): %d / %d photons; batch %d / %d\n', ...
                workersUsed, completedPhotons, config.Nphotons, batchID, batchCount);
            nextBatch = batchID + workersUsed;
            if nextBatch <= batchCount
                futures{slot} = parfeval(pool, @MC_RunBatch, 1, ...
                    modelConstant, tissue, config, counts(nextBatch), nextBatch);
            end
        end
    catch problem
        for k = 1:numel(futures)
            if ~isempty(futures{k})
                cancel(futures{k});
            end
        end
        rethrow(problem);
    end
    clear releaseModel;
end
