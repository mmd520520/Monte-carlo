function outputFiles = Step10_Plot(results, outputFile, visible)
% Raw central section plus slab averaging and spatial bin averaging.
% Average linear fluence BEFORE log10. Input results is unchanged.
if nargin<2, outputFile=fullfile(fileparts(mfilename('fullpath')),sprintf('knee_%d_fluence.png',results.Nphotons)); end
if nargin<3, visible=true; end
[~,iy]=min(abs(results.y));
displayPhi=results.fluenceWcm2; % complete MC field, including ALL air samples
raw=squeeze(displayPhi(:,iy,:))';
labels=squeeze(results.tissueLabels(:,iy,:))';
Render(raw,results.x,results.z,labels,results, ...
    'Raw central MC section: incident, reflected and escaping light included',outputFile,visible);
outputFiles={outputFile};
% Separate illustration only: never replace the full MC field in the main plot.
[folder,stem,ext]=fileparts(outputFile);
incidentFile=fullfile(folder,[stem '_incident_only' ext]);
incidentPhi=PlotIncidentAirBeam(results);
incidentSection=squeeze(incidentPhi(:,iy,:))';
Render(incidentSection,results.x,results.z,labels,results, ...
    'Illustration only: prescribed incident air beam; MC return light hidden',incidentFile,false);
outputFiles{end+1}=incidentFile;
factor=2; slabThickness=0.5; % cm: adjustable display slab, not a tissue change
if isfield(results,'options')
    if isfield(results.options,'plotBinFactor'), factor=results.options.plotBinFactor; end
    if isfield(results.options,'plotSlabThicknessCm'), slabThickness=results.options.plotSlabThicknessCm; end
end
if factor<=1, return; end
indices=find(abs(results.y)<=slabThickness/2+1e-12);
if isempty(indices), indices=iy; end
slab=squeeze(mean(displayPhi(:,indices,:),2));
% Partial final blocks are kept, including their true center coordinates.
nx=numel(results.x); nz=numel(results.z);
xb=zeros(1,ceil(nx/factor)); zb=zeros(1,ceil(nz/factor));
filtered=zeros(numel(zb),numel(xb));
for ix=1:numel(xb)
    rows=(ix-1)*factor+1:min(ix*factor,nx);
    xb(ix)=mean(results.x(rows));
    for iz=1:numel(zb)
        cols=(iz-1)*factor+1:min(iz*factor,nz);
        filtered(iz,ix)=mean(slab(rows,cols),'all');
        if ix==1, zb(iz)=mean(results.z(cols)); end
    end
end
[folder,stem,ext]=fileparts(outputFile);
binnedFile=fullfile(folder,[stem '_binned' ext]);
caption=sprintf('Full MC field: y slab %.3g cm; %d x %d bins; air returns included', ...
    numel(indices)*results.dy,factor,factor);
Render(filtered,xb,zb,labels,results,caption,binnedFile,visible);
outputFiles{end+1}=binnedFile;
end

function Render(data,x,z,labels,r,caption,filename,visible)
vis='off'; if visible, vis='on'; end
f=figure('Color','w','Visible',vis,'Position',[60 60 720 700]);
h=imagesc(x,z,log10(max(data,1e-8)));
set(h,'AlphaData',isfinite(data)&data>0); axis image;
set(gca,'YDir','reverse','Color',[.13 .13 .11]);
colormap(jet(256)); caxis([-5 0]); colorbar; hold on;
yline(r.source.z,'w--',sprintf('z = %g cm: incident plane',r.source.z));
% Geometry always comes from the original central voxel section.
% Knee exterior: boundary between all tissues (2,3,4) and air (1).
contour(r.x,r.z,double(labels>1),[.5 .5],'r','LineWidth',1.2);
for id=3:4
    contour(r.x,r.z,double(labels==id),[.5 .5],'r','LineWidth',1);
end
xlim([-10 10]); ylim([0 21]);
xlabel('x [cm]'); ylabel('depth z [cm]');
title(sprintf('%g nm | %d photons | log_{10}(fluence [W/cm^2])', ...
    r.source.wavelength,r.Nphotons));
subtitle({caption,'Literature proxies and interpolation; g and n assumed'});
exportgraphics(f,filename,'Resolution',180);
if ~visible, close(f); end
end

