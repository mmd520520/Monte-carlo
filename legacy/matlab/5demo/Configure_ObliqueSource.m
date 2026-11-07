function [source, reflectance] = Configure_ObliqueSource(source, tissue, thetaDeg, phiDeg)
    % 非偏振光从空气进入水平皮肤表面，thetaDeg相对于+z法线。
    %根据入射角、方位角设置光子的传播方向；
    %当前从空气发射，实际折射反射在边界处理。
    %step4_Main.m 22
    validateattributes(thetaDeg, {'numeric'}, {'scalar', 'real', 'finite', '>=', 0, '<', 90});
    validateattributes(phiDeg, {'numeric'}, {'scalar', 'real', 'finite'});
    theta = deg2rad(thetaDeg);
    phi = deg2rad(phiDeg);
    n1 = tissue(1).n;
    n2 = tissue(source.entryLabel).n;
    sinT = n1 / n2 * sin(theta);
    assert(sinT < 1, '入射界面全内反射，无法发射透射光。');
    thetaT = asin(sinT);
    ci = cos(theta);
    ct = cos(thetaT);
    Rs = ((n1 * ci - n2 * ct) / (n1 * ci + n2 * ct))^2;
    Rp = ((n2 * ci - n1 * ct) / (n2 * ci + n1 * ct))^2;
    reflectance = (Rs + Rp) / 2;
    source.uAir = [sin(theta) * cos(phi), sin(theta) * sin(phi), ci];
    source.uSpecular = [source.uAir(1:2), -ci];
    source.ux = sin(thetaT) * cos(phi);
    source.uy = sin(thetaT) * sin(phi);
    source.uz = ct;
    source.W0 = 1 - reflectance;
    source.thetaDeg = thetaDeg;
    source.phiDeg = phiDeg;
    source.thetaTissueDeg = rad2deg(thetaT);
    source.beamDefinition = 'collimated uniform disk above curved knee';
    if isfield(source,'launchFromAir') && source.launchFromAir
        source.ux=source.uAir(1); source.uy=source.uAir(2); source.uz=source.uAir(3);
        source.W0=1; reflectance=0;
        % Refraction and reflection occur at the actual air/tissue voxel faces.
        source.thetaTissueDeg=NaN;
    end
end
