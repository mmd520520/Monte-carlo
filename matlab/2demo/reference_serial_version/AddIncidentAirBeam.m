function results = AddIncidentAirBeam(results)
    % Analytic incident fluence in nonabsorbing air, per unit incident power.
    % Combine analytic incident/specular beams with MC diffuse air path lengths.
    % Rebuild from separate components on each call to avoid double counting.
    if ~isfield(results, 'source')
        % Compatibility with the original saved 500-nm, 1-mm-diameter run.
        results.source = struct('x', 0, 'y', 0, 'z', 1, 'radius', 0.5, ...
            'type', 'uniform_disk', 'ux', 0, 'uy', 0, 'uz', 1, 'wavelength', 500);
    end
    s = results.source;
    assert(strcmp(s.type, 'uniform_disk') && s.ux == 0 && s.uy == 0 && s.uz == 1);
    ny = size(results.Phi, 2);
    dx = results.x(2)-results.x(1);
    dz = results.z(2)-results.z(1);
    if isfield(results, 'dy')
        dy = results.dy;
    else
        dy = dx;
    end
    % Original x and z vectors denote upper voxel faces, not cell centers.
    xc = results.x(:)-dx/2;
    yc = ((1:ny)-ny/2)*dy-dy/2;
    beam = ((xc-s.x).^2+(yc-s.y).^2 <= s.radius^2)/(pi*s.radius^2);
    airLayers = find(results.z(:)-dz/2 < s.z);
    for iz = airLayers'
        if isfield(results, 'specular')
            spec = results.specular;
        else
            spec = 0;
        end
        results.Phi(:, :, iz) = (1+spec)*beam;
        if isfield(results, 'airDiffusePhi')
            results.Phi(:, :, iz) = results.Phi(:, :, iz)+results.airDiffusePhi(:, :, iz);
        end
    end
    if isfield(results, 'airDiffusePhi')
        results.airFluenceModel = 'incident + specular + MC escaping-ray path length';
    else
        results.airFluenceModel = 'incident + specular only; diffuse paths unavailable';
    end
    results.airBeamIntegral = sum(beam(:))*dx*dy;
end
