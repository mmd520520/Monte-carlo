function results = Step9_Output(tallies, model, tissue, config)
    % 第9步。输入原始累计、模型、参数、配置；输出归一化结果，不写文件。
    n = config.Nphotons;
    v = config.voxelVolume;
    assert(tallies.Nlaunched == n && tallies.Nterminated == n);
    results.absorbedFraction = sum(tallies.Araw(:))/n;%吸收比例
    results.reflectance = sum(tallies.Rraw(:))/n;%从计算区域顶部逃出的能量比例
    results.transmittance = sum(tallies.Traw(:))/n;%从计算区域底部逃出的能量比例
    results.sideEscape = tallies.sideEscapeRaw/n;%从计算区域四周侧面逃出的能量比例
    results.specular = config.Rsp;%发射时预先扣除的镜面反射比例
    results.energyTotal = results.absorbedFraction+results.reflectance+ ...
        results.transmittance+results.sideEscape+results.specular;%能力总和（模拟计算）
    results.rouletteCorrection = tallies.rouletteBalanceRaw/n;%轮盘能量归一化
    results.bookkeepingTotal = results.energyTotal+results.rouletteCorrection;%
    assert(abs(results.bookkeepingTotal-1) < 1e-8, '能量收支检查失败。');
    assert(all(isfinite(tallies.Araw(:))) && all(tallies.Araw(:) >= 0));
    results.A = tallies.Araw/(n*v);  %吸收功率密度
    results.Phi = nan(model.size); %%构建布尔矩阵
    for id = 2:numel(tissue)
        mask = model.T == id;
        results.Phi(mask) = results.A(mask)/tissue(id).mua;%fluence  A是光子能量浓度 Phi是注入量
    end
    %%
    results.R = tallies.Rraw/(n*config.surfaceArea);
    results.T = tallies.Traw/(n*config.surfaceArea);
    results.airDiffusePhi = tallies.AirPathRaw/(n*v);
    airMask=model.T==1;
    results.Phi(airMask)=results.airDiffusePhi(airMask);
    results.airFieldTracked=true;
    results.airFluenceModel='Full-volume MC path length, including incident rays';
    results.escapeDefinition='R/T/side: escapes through computational-box top/bottom/sides; specular is included stochastically';
    results.airEscapedPackets = tallies.airEscapedPackets;
    %%
    results.Nphotons = n;
    results.seed = config.seed;
    results.boundaryEvents = tallies.boundaryEvents;
    results.scatteringEvents = tallies.scatteringEvents;%散射和边界事件次数
    results.x = model.x;
    results.z = model.z;
    results.dy = model.dy;
    results.y = model.y;
    results.lengthUnit = 'cm';
    results.tissueLabels = model.T;
    results.tissue = tissue;
    results.parameterNote = 'Literature-informed proxies and wavelength interpolation; g and n assumed; not subject-calibrated';
    results.fluenceWcm2 = results.Phi * config.source.power;
    results.powerW = config.source.power;
    results.source = config.source;
    if isfield(config, 'options')
        results.options = config.options;
    end
    results = AddIncidentAirBeam(results);
    results.fluenceWcm2 = results.Phi * config.source.power;
end
