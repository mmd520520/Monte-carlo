function options = MC_Settings(userOptions)
    % 运行选项；角度单位为度。皮肤表面圆形光斑的直径保持不变。
    options = struct('useParallel', true, 'numWorkers', 4, ...
        'batchSize', 5000, 'thetaDeg', 0, 'phiDeg', 0, 'plotBinFactor', 5);
    if nargin >= 1 && ~isempty(userOptions)
        assert(isstruct(userOptions) && isscalar(userOptions));
        names = fieldnames(userOptions);
        for k = 1:numel(names)
            name = names{k};
            assert(isfield(options, name), '未知选项：%s', name);
            options.(name) = userOptions.(name);
        end
    end
    validateattributes(options.useParallel, {'logical'}, {'scalar'});
    validateattributes(options.numWorkers, {'numeric'}, {'scalar', 'integer', 'positive', 'finite'});
    validateattributes(options.batchSize, {'numeric'}, {'scalar', 'integer', 'positive', 'finite'});
    validateattributes(options.thetaDeg, {'numeric'}, {'scalar', 'real', 'finite', '>=', 0, '<', 90});
    validateattributes(options.phiDeg, {'numeric'}, {'scalar', 'real', 'finite'});
    validateattributes(options.plotBinFactor, {'numeric'}, {'scalar', 'integer', 'positive', 'finite'});
end
