function photon = Step4_Launch(source, model)
    % 在皮肤表面的圆形光斑内采样，再沿折射方向进入组织。
    radius = source.radius * sqrt(rand);
    azimuth = 2 * pi * rand;
    surfacePoint = [source.x + radius * cos(azimuth), ...
        source.y + radius * sin(azimuth), source.z];
    if isfield(source,'launchFromAir') && source.launchFromAir
        surfacePoint(3)=source.emissionZ;
    end
    photon.u = [source.ux, source.uy, source.uz];
    inwardLength = (source.zLaunch - surfacePoint(3)) / photon.u(3);
    photon.p = surfacePoint + inwardLength * photon.u;
    photon.idx = floor((photon.p + model.offset) ./ model.spacing) + 1;
    assert(all(photon.idx >= 1 & photon.idx <= model.size));
    photon.weight = source.W0;
    photon.alive = true;
    photon.label = double(model.T(photon.idx(1), photon.idx(2), photon.idx(3)));
    if isfield(source,'launchFromAir') && source.launchFromAir
        assert(photon.label==1,'Emission point must be in air.');
    else
        assert(photon.label>1,'Emission point must be inside tissue.');
    end
end

