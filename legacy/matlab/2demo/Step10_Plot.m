function outputFiles = Step10_Plot(results, outputFile, visible)
    % 绘图不改变results.Phi；坐标取体素中心，分箱坐标按实际尺寸计算。
    if nargin < 2
        outputFile = fullfile(fileparts(mfilename('fullpath')), 'fluence_section.png');
    end
    if nargin < 3
        visible = true;
    end
    results = AddIncidentAirBeam(results);
    nx = size(results.Phi, 1);
    nz = size(results.Phi, 3);
    dx = results.x(2) - results.x(1);
    dz = results.z(2) - results.z(1);
    xCenter = results.x - dx / 2;
    zCenter = results.z - dz / 2;
    iy = round(size(results.Phi, 2) / 2);
    section = squeeze(results.Phi(:, iy, :))';
    caption = 'Single y slice; air includes incident, specular and escaping rays';
    Render_Section(section, xCenter, zCenter, results, caption, outputFile, visible);
    outputFiles = {outputFile};

    factor = 5;
    if isfield(results, 'options')
        factor = results.options.plotBinFactor;
    end
    if factor > 1 && nx >= 100 && mod(nx, factor) == 0 && mod(nz, factor) == 0
        ny = size(results.Phi, 2);
        yCenter = ((1:ny) - ny / 2) * results.dy - results.dy / 2;
        slabIndices = find(abs(yCenter) <= 0.1 + 1e-12);
        slab = squeeze(mean(results.Phi(:, slabIndices, :), 2));
        temporary = reshape(slab, factor, nx / factor, factor, nz / factor);
        binned = squeeze(mean(mean(temporary, 1), 3))';
        xBinned = mean(reshape(xCenter, factor, nx / factor), 1);
        zBinned = mean(reshape(zCenter, factor, nz / factor), 1);
        [folder, stem, extension] = fileparts(outputFile);
        binnedFile = fullfile(folder, [stem, '_binned', extension]);
        caption = sprintf('y slab %.3f mm; display bins %.3f x %.3f mm', ...
            numel(slabIndices) * results.dy, factor * dx, factor * dz);
        Render_Section(binned, xBinned, zBinned, results, caption, binnedFile, visible);
        outputFiles{end + 1} = binnedFile;
    end
end

function Render_Section(data, xAxis, zAxis, results, caption, outputFile, visible)
    if visible
        visibility = 'on';
    else
        visibility = 'off';
    end
    data(data <= 0) = NaN;
    figureHandle = figure('Color', 'w', 'Visible', visibility, ...
        'Position', [50, 50, 550, 440]);
    imageHandle = imagesc(xAxis, zAxis, log10(data));
    set(imageHandle, 'AlphaData', isfinite(data));
    set(gca, 'YDir', 'reverse', 'Color', [0.93, 0.93, 0.93], 'FontSize', 12);
    axis image;
    xlim([-1.5, 1.5]);
    ylim([0, 3]);
    clim([-4, 1]);
    colormap(jet(256));
    cb = colorbar;
    cb.Label.String = 'log_{10}(fluence [mm^{-2}])';
    xlabel('x [mm]');
    ylabel('z [mm]');
    hold on;
    theta = linspace(0, 2 * pi, 300);
    plot(0.5 * cos(theta), 2 + 0.5 * sin(theta), 'k--', 'LineWidth', 1.3);
    yline(1, 'k:');
    yline(1.1, 'k:');
    angle = 0;
    azimuth = 0;
    if isfield(results.source, 'thetaDeg')
        angle = results.source.thetaDeg;
        azimuth = results.source.phiDeg;
    end
    title(sprintf('%g nm | N=%g | air angle=%.1f deg, azimuth=%.1f deg', ...
        results.source.wavelength, results.Nphotons, angle, azimuth));
    subtitle({caption, 'Gray = zero or unsampled; original 3-D array unchanged'});
    exportgraphics(figureHandle, outputFile, 'Resolution', 180);
    if ~visible
        close(figureHandle);
    end
end
