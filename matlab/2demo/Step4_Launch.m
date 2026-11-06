function photon = Step4_Launch(source, model)
    % 在皮肤表面的圆形光斑内采样，再沿折射方向进入组织。
    radius = source.radius * sqrt(rand);
    azimuth = 2 * pi * rand;
    surfacePoint = [source.x + radius * cos(azimuth), ...
        source.y + radius * sin(azimuth), source.z];
    photon.u = [source.ux, source.uy, source.uz];
    inwardLength = (source.zLaunch - source.z) / photon.u(3);
    photon.p = surfacePoint + inwardLength * photon.u;
    photon.idx = floor((photon.p + model.offset) ./ model.spacing) + 1;
    assert(all(photon.idx >= 1 & photon.idx <= model.size));
    photon.weight = source.W0;
    photon.alive = true;
    photon.label = double(model.T(photon.idx(1), photon.idx(2), photon.idx(3)));
    assert(photon.label == 5, '发射点不在表皮，请检查表面几何。');
end
