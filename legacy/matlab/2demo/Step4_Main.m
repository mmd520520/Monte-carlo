function results = Step4_Main(photonCount, smokeTest, seed, saveResults, userOptions)
    % 示例：options=struct('numWorkers',4,'thetaDeg',30,'phiDeg',0);
    % results=Step4_Main(10000,false,1,true,options);
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
    if nargin < 5
        userOptions = struct;
    end
    options = MC_Settings(userOptions);
    [model, tissue, config, tallies] = Prepare_Inputs(photonCount, smokeTest, seed);
    validateattributes(seed, {'numeric'}, {'<', 2^32});
    [config.source, config.Rsp] = Configure_ObliqueSource( ...
        config.source, tissue, options.thetaDeg, options.phiDeg);
    config.options = options;
    assert(config.source.radius + abs(config.source.x) < model.Nx * model.dx / 2);
    assert(config.source.radius + abs(config.source.y) < model.Ny * model.dy / 2);
    fprintf('Air incidence %.2f deg; azimuth %.2f deg; tissue angle %.2f deg; Rsp %.6f\n', ...
        options.thetaDeg, options.phiDeg, config.source.thetaTissueDeg, config.Rsp);
    timer = tic;
    [tallies, workersUsed, batchCount] = MC_RunBatches( ...
        model, tissue, config, tallies, options);
    results = Step9_Output(tallies, model, tissue, config);
    results.elapsedSeconds = toc(timer);
    results.smokeTest = smokeTest;
    results.options = options;
    results.workersUsed = workersUsed;
    results.batchCount = batchCount;
    results.randomGenerator = 'mrg32k3a; independent substream per batch';
    fprintf('Energy sum %.10f; with roulette correction %.10f\n', ...
        results.energyTotal, results.bookkeepingTotal);
    fprintf('Elapsed %.2f seconds\n', results.elapsedSeconds);
    if saveResults
        if smokeTest
            name = 'mc_smoke_results.mat';
        else
            name = 'mc_results.mat';
        end
        save(fullfile(fileparts(mfilename('fullpath')), name), 'results', '-v7.3');
    end
end
