function photon = Step4_Launch(source, model)
    % 发射单个光子包；均匀圆光斑采用sqrt(rand)采样半径。
    r = source.radius*sqrt(rand);
    angle = 2*pi*rand;
    photon.p = [source.x+r*cos(angle), source.y+r*sin(angle), source.zLaunch];
    photon.u = [source.ux source.uy source.uz];
    photon.idx = floor((photon.p+model.offset)./model.spacing)+1;
    assert(all(photon.idx >= 1 & photon.idx <= model.size));
    photon.weight = source.W0;
    photon.alive = true;
    photon.label = double(model.T(photon.idx(1), photon.idx(2), photon.idx(3)));
end
