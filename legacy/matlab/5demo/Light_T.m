% All lengths in cm; input coefficients in cm^-1.
Nphotons=2000;
voxelVolume=dx*dy*dz; surfaceArea=dx*dy;
source=struct('wavelength',wavelength,'type','uniform_disk', ...
    'diameter',8,'radius',4,'x',0,'y',0,'z',zsurf, ...
    'ux',0,'uy',0,'uz',1,'entryLabel',2);
% source.irradiance=20; % W/cm^2
% source.power=source.irradiance*pi*source.radius^2;
source.power=20; % 总光功率，W
source.irradiance=source.power/(pi*source.radius^2); % W/cm^2
Rsp=((tissue(1).n-tissue(2).n)/(tissue(1).n+tissue(2).n))^2;
% Emit above the curved knee; entry Fresnel is handled at actual voxel faces.
% source.z=4 is the nominal knee contact depth; emission plane is z=0.
source.launchFromAir=true; source.emissionZ=0;
Rsp=0; source.W0=1; source.zLaunch=source.emissionZ+1e-9;
roulette=struct('threshold',.001,'chance',.10);
boundary=struct('top','escape','bottom','escape','side','escape');
Araw=zeros(Nx,Ny,Nz); Rraw=zeros(Nx,Ny); Traw=zeros(Nx,Ny);
sideEscapeRaw=0; Nlaunched=0; Nterminated=0;

