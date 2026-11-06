function report=Compare_SpotSize1(diametersCm,photonCount,repeats,outputDir,useParallel)

% Fixed-total-power spot-size comparison. Only this new file is required.

% Run in the same folder as Prepare_Inputs.m and the other simulation files.

% Examples:

%   report=Compare_SpotSize1;

%   report=Compare_SpotSize1([1 2 4 6 8],100000,5);

% H = fluence rate * exposure time, NOT absorbed energy density.

% Defaults: 20 W, 300 s, current wavelength/optical parameters, normal incidence.

% 1. 设置光斑直径、每次光子数、重复次数和结果保存位置。

if nargin<1 || isempty(diametersCm), diametersCm=[1 2 5 10]; end

if nargin<2 || isempty(photonCount), photonCount=10000; end

if nargin<3 || isempty(repeats), repeats=3; end

if nargin<4 || isempty(outputDir)

 outputDir=fullfile(fileparts(mfilename('fullpath')),'spot_size_results1');

end

if nargin<5 || isempty(useParallel), useParallel=true; end

validateattributes(diametersCm,{'numeric'},{'vector','real','positive','finite'});

validateattributes(photonCount,{'numeric'},{'scalar','integer','positive','finite'});

validateattributes(repeats,{'numeric'},{'scalar','integer','>=',2});

validateattributes(useParallel,{'logical'},{'scalar'});

if ~exist(outputDir,'dir'), mkdir(outputDir); end

diametersCm=diametersCm(:)';

% 固定总功率20 W、照射300秒；深度从中心轴的皮肤表面向下计算。

powerW=20; exposureSeconds=300; depthsCm=[1 2 5 10]; roiSideCm=.5;

options=MC_Settings(struct('useParallel',useParallel,'numWorkers',4, ...
'batchSize',1000,'thetaDeg',0,'phiDeg',0,'plotBinFactor',1));

% 2. 调用原有函数建立模型及光学参数，不修改原函数。

[model,tissue,config,initial]=Prepare_Inputs(photonCount,false,1);

clear initial;

% 波长从光学参数文件读取；吸收、散射参数应与该波长配套。

validateattributes(config.source.wavelength,{'numeric'},{'scalar','positive','finite'});

assert(config.source.x==0 && config.source.y==0,'This comparison targets the x=y=0 axis.');

assert(all(diametersCm/2<min(model.Nx*model.dx,model.Ny*model.dy)/2), ...
 'A requested source disk reaches outside the computational box.');

% 3. 找到中心皮肤表面，定位皮下1、2、5、10 cm的目标点。

[~,ix]=min(abs(model.x)); [~,iy]=min(abs(model.y));

iz=find(squeeze(model.T(ix,iy,:))>1,1);

skinZ=model.z(iz)-model.dz/2;

targetZ=skinZ+depthsCm;

assert(all(targetZ<max(model.z)),'A target is outside the model.');

mu=zeros(model.size);

for id=2:numel(tissue), mu(model.T==id)=tissue(id).mua; end

mu(model.T==1)=NaN;

% 点值由相邻8个体素插值得到；另计算0.5 cm小立方体平均值辅助观察噪声。

roiIndices=cell(1,numel(depthsCm));

pointIndices=cell(1,numel(depthsCm));

for j=1:numel(depthsCm)

 rx=find(abs(model.x)<roiSideCm/2+1e-12);

 ry=find(abs(model.y)<roiSideCm/2+1e-12);

 rz=find(abs(model.z-targetZ(j))<roiSideCm/2+1e-12);

 [xx,yy,zz]=ndgrid(rx,ry,rz);

 ids=sub2ind(model.size,xx(:),yy(:),zz(:));

 assert(all(model.T(ids)>1),'ROI contains air; choose a smaller ROI.');

 roiIndices{j}=ids;

 % The exact axis/grid-boundary targets lie halfway between voxel centers.

 px=find(abs(model.x)<=model.dx/2+1e-12);

 py=find(abs(model.y)<=model.dy/2+1e-12);

 pz=find(abs(model.z-targetZ(j))<=model.dz/2+1e-12);

 [xx,yy,zz]=ndgrid(px,py,pz);

 pointIndices{j}=sub2ind(model.size,xx(:),yy(:),zz(:));

 assert(numel(pointIndices{j})==8,'Expected 8 neighboring voxel centers.');

 assert(all(model.T(pointIndices{j})>1),'Target interpolation includes air.');

end

ns=numel(diametersCm); nd=numel(depthsCm);

pointH=zeros(ns,nd,repeats); roiH=pointH; occupied=zeros(ns,nd,repeats);

energy=zeros(ns,repeats);

timer=tic;

% 4. 逐个光斑进行多次独立仿真；改变光斑时固定总功率，并重新计算辐照度。

for i=1:ns

 for r=1:repeats

  config.Nphotons=photonCount; config.seed=1000+r;

  config.source.diameter=diametersCm(i); config.source.radius=diametersCm(i)/2;

  config.source.power=powerW;

  config.source.irradiance=powerW/(pi*config.source.radius^2);

  [config.source,config.Rsp]=Configure_ObliqueSource(config.source,tissue,0,0);

  config.options=options;

  fprintf('\nDiameter %.2f cm; repeat %d/%d; %.6g W/cm^2; total %.6g W\n', ...
   diametersCm(i),r,repeats,config.source.irradiance,powerW);

  tallies=MC_CreateTallies(model);

  [tallies,~,~]=MC_RunBatches(model,tissue,config,tallies,options);

  assert(tallies.Nlaunched==photonCount && tallies.Nterminated==photonCount);
  energy(i,r)=(sum(tallies.Araw(:))+sum(tallies.Rraw(:))+sum(tallies.Traw(:))+ ...
   tallies.sideEscapeRaw+tallies.rouletteBalanceRaw)/photonCount+config.Rsp;

  assert(abs(energy(i,r)-1)<1e-8,'Energy balance failed.');

  % Same estimator as Step9_Output, restricted to target voxels to save memory.

  % 5. 吸收权重除以光子数、体素体积和吸收系数，再乘功率及时间，得到J/cm^2。

  scale=powerW*exposureSeconds/(photonCount*config.voxelVolume);

  for j=1:nd

   ids=pointIndices{j};

   pointH(i,j,r)=mean(tallies.Araw(ids)./mu(ids))*scale;

   occupied(i,j,r)=nnz(tallies.Araw(ids));

   ids=roiIndices{j};

   roiH(i,j,r)=mean(tallies.Araw(ids)./mu(ids))*scale;

  end

  clear tallies;

 end

 % Save completed diameters so interrupted runs retain their completed results.

 save(fullfile(outputDir,'spot_scan_checkpoint.mat'),'pointH','roiH','occupied', ...
  'diametersCm','depthsCm','targetZ','skinZ','photonCount','repeats','energy', ...
  'powerW','exposureSeconds','roiSideCm','i');

end

% 6. 计算均值和标准误差，标记采样不足的数据，并导出表格、MAT文件和图片。

report=struct('diametersCm',diametersCm,'depthsCm',depthsCm,'targetZ',targetZ, ...
 'skinZ',skinZ,'wavelengthNm',config.source.wavelength,'powerW',powerW,'exposureSeconds',exposureSeconds, ...
 'photonCountPerRepeat',photonCount,'repeats',repeats, ...
 'pointH',pointH,'roiH',roiH,'occupiedPointVoxels',occupied, ...
 'roiSideCm',roiSideCm,'energy',energy,'elapsedSeconds',toc(timer));

report.pointMean=mean(pointH,3); report.pointSE=std(pointH,0,3)/sqrt(repeats);

report.roiMean=mean(roiH,3); report.roiSE=std(roiH,0,3)/sqrt(repeats);

% A warning flag is a screening rule, not a proof of statistical convergence.

report.pointLowSampling=any(pointH==0,3) | any(occupied<8,3) | ...
 report.pointSE>.3*report.pointMean;

report.roiLowSampling=any(roiH==0,3) | report.roiSE>.3*report.roiMean;

rows=ns*nd;

DiameterCm=zeros(rows,1);DepthBelowSkinCm=DiameterCm;TargetZCm=DiameterCm;

IncidentIrradianceWcm2=DiameterCm;PointH_Jcm2=DiameterCm;PointSE_Jcm2=DiameterCm;

RoiH_Jcm2=DiameterCm;RoiSE_Jcm2=DiameterCm;

PointLowSampling=false(rows,1);RoiLowSampling=PointLowSampling;

for i=1:ns

 for j=1:nd

  k=(i-1)*nd+j;DiameterCm(k)=diametersCm(i);DepthBelowSkinCm(k)=depthsCm(j);

  TargetZCm(k)=targetZ(j);IncidentIrradianceWcm2(k)=powerW/(pi*(diametersCm(i)/2)^2);

  PointH_Jcm2(k)=report.pointMean(i,j);PointSE_Jcm2(k)=report.pointSE(i,j);

  RoiH_Jcm2(k)=report.roiMean(i,j);RoiSE_Jcm2(k)=report.roiSE(i,j);

  PointLowSampling(k)=report.pointLowSampling(i,j);RoiLowSampling(k)=report.roiLowSampling(i,j);

 end

end

report.summary=table(DiameterCm,DepthBelowSkinCm,TargetZCm,IncidentIrradianceWcm2, ...
 PointH_Jcm2,PointSE_Jcm2,PointLowSampling,RoiH_Jcm2,RoiSE_Jcm2,RoiLowSampling);
writetable(report.summary,fullfile(outputDir,'spot_size_summary.csv'));

save(fullfile(outputDir,'spot_size_report.mat'),'report');

% 画图：四个子图分别显示四个深度的中心点累计光注量。
figure;
for j=1:nd
    subplot(2,2,j);
    plot(diametersCm,report.pointMean(:,j),'o-');
    xlabel('光斑直径 [cm]');
    ylabel('累计光注量 [J/cm^2]');
    title(sprintf('皮下 %g cm',depthsCm(j)));
    grid on;
end
saveas(gcf,fullfile(outputDir,'spot_size_comparison.png'));

fprintf('\nH [J/cm^2], axis-point estimates (check PointLowSampling flags):\n');

disp(report.summary);

fprintf('Outputs: %s\nElapsed %.1f s\n',outputDir,report.elapsedSeconds);

end

