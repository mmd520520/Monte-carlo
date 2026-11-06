function results = AddIncidentAirBeam(results)
    % 由独立分量重建空气总光场，重复调用不会重复叠加。
    % 兼容旧结果，在未追踪空气光路时补建空气光场。
    % 当前程序已追踪空气光路，调用它会直接返回，不做修改。
    if isfield(results,'airFieldTracked') && results.airFieldTracked
        return; % Air path estimator already includes all incident/reflected rays.
    end
    source = results.source;
    if ~isfield(source, 'uAir')
        source.uAir = [0, 0, 1];
    end
    incoming = source.uAir;
    reflected = [incoming(1:2), -incoming(3)];
    assert(incoming(3) > 0);
    ny = size(results.Phi, 2);
    dx = results.x(2) - results.x(1);
    dz = results.z(2) - results.z(1);
    xCenter = results.x(:);
    yCenter = results.y(:)';
    area = pi * source.radius^2;
    % 表面圆形光斑：标量光通量=法向照度/cos(theta)。
    scale = 1 / (area * incoming(3));
    airLayers = find(results.z(:) < source.z);
    for iz = airLayers'
        height = results.z(iz);
        travelIn = (source.z - height) / incoming(3);
        surfaceX = xCenter + travelIn * incoming(1);
        surfaceY = yCenter + travelIn * incoming(2);
        incidentMask = (surfaceX - source.x).^2 + ...
            (surfaceY - source.y).^2 <= source.radius^2;
        travelOut = (height - source.z) / reflected(3);
        surfaceX = xCenter - travelOut * reflected(1);
        surfaceY = yCenter - travelOut * reflected(2);
        specularMask = (surfaceX - source.x).^2 + ...
            (surfaceY - source.y).^2 <= source.radius^2;
        results.Phi(:, :, iz) = scale * ...
            (double(incidentMask) + results.specular * double(specularMask));
        if isfield(results, 'airDiffusePhi')
            results.Phi(:, :, iz) = results.Phi(:, :, iz) + results.airDiffusePhi(:, :, iz);
        end
    end
    results.airFluenceModel = 'oblique incident + specular + MC escaping-ray path length';
end
