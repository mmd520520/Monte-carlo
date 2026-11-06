function results = Step9_Output(tallies, model, tissue, config)
    % 第9步。输入原始累计、模型、参数、配置；输出归一化结果，不写文件。
    n = config.Nphotons;
    v = config.voxelVolume;
    assert(tallies.Nlaunched == n && tallies.Nterminated == n);
    results.absorbedFraction = sum(tallies.Araw(:))/n;
    results.reflectance = sum(tallies.Rraw(:))/n;
    results.transmittance = sum(tallies.Traw(:))/n;
    results.sideEscape = tallies.sideEscapeRaw/n;
    results.specular = config.Rsp;
    results.energyTotal = results.absorbedFraction+results.reflectance+ ...
        results.transmittance+results.sideEscape+results.specular;
    results.rouletteCorrection = tallies.rouletteBalanceRaw/n;
    results.bookkeepingTotal = results.energyTotal+results.rouletteCorrection;
    assert(abs(results.bookkeepingTotal-1) < 1e-8, '能量收支检查失败。');
    assert(all(isfinite(tallies.Araw(:))) && all(tallies.Araw(:) >= 0));
    results.A = tallies.Araw/(n*v);
    results.Phi = nan(model.size);
    for id = [3 4 5]
        mask = model.T == id;
        results.Phi(mask) = results.A(mask)/tissue(id).mua;
    end
    results.R = tallies.Rraw/(n*config.surfaceArea);
    results.T = tallies.Traw/(n*config.surfaceArea);
    results.airDiffusePhi = tallies.AirPathRaw/(n*v);
    results.airEscapedPackets = tallies.airEscapedPackets;
    results.Nphotons = n;
    results.seed = config.seed;
    results.boundaryEvents = tallies.boundaryEvents;
    results.scatteringEvents = tallies.scatteringEvents;
    results.x = model.x;
    results.z = model.z;
    results.dy = model.dy;
    results.source = config.source;
    if isfield(config, 'options')
        results.options = config.options;
    end
    results = AddIncidentAirBeam(results);
end
