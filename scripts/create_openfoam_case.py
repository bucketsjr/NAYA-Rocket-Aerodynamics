#!/usr/bin/env python3
"""Create an explicitly unverified OpenFOAM.com simpleFoam/SST starter case.

This is a template requiring meshing/solver validation on a machine running
OpenFOAM. It is NOT an executed or verified 3D RANS CFD result.
"""
from pathlib import Path
from shutil import copy2

root=Path(__file__).resolve().parents[1]
case=root/'openfoam'/'naya_external'
files={
'0/U':r'''dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (15 0 0);
boundaryField
{
    inlet    { type fixedValue; value uniform (15 0 0); }
    outlet   { type inletOutlet; inletValue uniform (15 0 0); value uniform (15 0 0); }
    farfield { type fixedValue; value uniform (15 0 0); }
    rocket   { type noSlip; }
}
''',
'0/p':r'''dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    inlet    { type zeroGradient; }
    outlet   { type fixedValue; value uniform 0; }
    farfield { type zeroGradient; }
    rocket   { type zeroGradient; }
}
''',
'0/k':r'''dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0.03375;
boundaryField
{
    inlet    { type fixedValue; value uniform 0.03375; }
    outlet   { type inletOutlet; inletValue uniform 0.03375; value uniform 0.03375; }
    farfield { type fixedValue; value uniform 0.03375; }
    rocket   { type kqRWallFunction; value uniform 0.03375; }
}
''',
'0/omega':r'''dimensions      [0 0 -1 0 0 0 0];
internalField   uniform 4;
boundaryField
{
    inlet    { type fixedValue; value uniform 4; }
    outlet   { type inletOutlet; inletValue uniform 4; value uniform 4; }
    farfield { type fixedValue; value uniform 4; }
    rocket   { type omegaWallFunction; value uniform 4; }
}
''',
'0/nut':r'''dimensions      [0 2 -1 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    inlet    { type calculated; value uniform 0; }
    outlet   { type calculated; value uniform 0; }
    farfield { type calculated; value uniform 0; }
    rocket   { type nutkWallFunction; value uniform 0; }
}
''',
'constant/transportProperties':r'''transportModel  Newtonian;
nu              [0 2 -1 0 0 0 0] 1.5e-05;
''',
'constant/turbulenceProperties':r'''simulationType RAS;
RAS
{
    RASModel        kOmegaSST;
    turbulence      on;
    printCoeffs     on;
}
''',
'system/blockMeshDict':r'''scale 1;
vertices
(
    (-1.8 -0.72 -0.72)
    ( 2.2 -0.72 -0.72)
    ( 2.2  0.72 -0.72)
    (-1.8  0.72 -0.72)
    (-1.8 -0.72  0.72)
    ( 2.2 -0.72  0.72)
    ( 2.2  0.72  0.72)
    (-1.8  0.72  0.72)
);
blocks
(
    hex (0 1 2 3 4 5 6 7) (80 32 32) simpleGrading (1 1 1)
);
edges ();
boundary
(
    inlet    { type patch; faces ((0 4 7 3)); }
    outlet   { type patch; faces ((1 2 6 5)); }
    farfield { type patch; faces ((0 1 5 4) (3 7 6 2) (0 3 2 1) (4 5 6 7)); }
);
mergePatchPairs ();
''',
'system/surfaceFeatureExtractDict':r'''naya_concept.stl
{
    extractionMethod extractFromSurface;
    extractFromSurfaceCoeffs { includedAngle 150; }
    writeObj yes;
}
''',
'system/snappyHexMeshDict':r'''castellatedMesh true;
snap            true;
addLayers       false;  // Starter only: wall-resolved study needs y+ and layer design.
geometry
{
    naya_concept.stl { type triSurfaceMesh; name rocket; }
};
castellatedMeshControls
{
    maxLocalCells 2000000;
    maxGlobalCells 4500000;
    minRefinementCells 0;
    maxLoadUnbalance 0.10;
    nCellsBetweenLevels 3;
    features
    (
        { file "naya_concept.eMesh"; level 4; }
    );
    refinementSurfaces
    {
        rocket
        {
            level (3 4);
            patchInfo { type wall; }
        }
    }
    resolveFeatureAngle 30;
    refinementRegions {}
    locationInMesh (-1.4 0.6 0.6);
    allowFreeStandingZoneFaces true;
}
snapControls
{
    nSmoothPatch 3;
    tolerance 2.0;
    nSolveIter 30;
    nRelaxIter 5;
    nFeatureSnapIter 10;
    implicitFeatureSnap false;
    explicitFeatureSnap true;
    multiRegionFeatureSnap false;
}
addLayersControls
{
    relativeSizes true;
    layers { rocket { nSurfaceLayers 0; } }
    expansionRatio 1.2;
    finalLayerThickness 0.3;
    minThickness 0.1;
    nGrow 0;
    featureAngle 60;
    slipFeatureAngle 30;
    nRelaxIter 3;
    nSmoothSurfaceNormals 1;
    nSmoothNormals 3;
    nSmoothThickness 10;
    maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3;
    minMedialAxisAngle 90;
    nBufferCellsNoExtrude 0;
    nLayerIter 50;
}
meshQualityControls
{
    maxNonOrtho 65;
    maxBoundarySkewness 20;
    maxInternalSkewness 4;
    maxConcave 80;
    minVol 1e-13;
    minTetQuality 1e-15;
    minArea -1;
    minTwist 0.02;
    minDeterminant 0.001;
    minFaceWeight 0.02;
    minVolRatio 0.01;
    minTriangleTwist -1;
    nSmoothScale 4;
    errorReduction 0.75;
}
debug 0;
mergeTolerance 1e-6;
''',
'system/fvSchemes':r'''ddtSchemes { default steadyState; }
gradSchemes { default Gauss linear; }
divSchemes
{
    default none;
    div(phi,U) bounded Gauss linearUpwind grad(U);
    div(phi,k) bounded Gauss upwind;
    div(phi,omega) bounded Gauss upwind;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes { default corrected; }
wallDist { method meshWave; }
''',
'system/fvSolution':r'''solvers
{
    p { solver GAMG; tolerance 1e-7; relTol 0.05; smoother GaussSeidel; }
    "(U|k|omega)" { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-7; relTol 0.1; }
}
SIMPLE
{
    nNonOrthogonalCorrectors 1;
    residualControl
    {
        p 1e-5;
        U 1e-5;
        "(k|omega)" 1e-5;
    }
}
relaxationFactors
{
    fields { p 0.3; }
    equations { U 0.7; k 0.7; omega 0.7; }
}
''',
'system/controlDict':r'''application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         1500;
deltaT          1;
writeControl    timeStep;
writeInterval   250;
purgeWrite      3;
writeFormat     ascii;
writePrecision  8;
runTimeModifiable true;
functions
{
    forceSummary
    {
        type forces;
        libs ("libforces.so");
        patches (rocket);
        p p;
        U U;
        rho rhoInf;
        rhoInf 1.225;
        CofR (0 0 0);
        log true;
        writeControl timeStep;
        writeInterval 10;
    }
}
''',
}

def mk():
    for path,body in files.items():
        f=case/path;f.parent.mkdir(parents=True,exist_ok=True)
        if path.startswith('0/'):cls='volVectorField' if path=='0/U' else 'volScalarField'
        else:cls='dictionary'
        header=(f'FoamFile\n{{\n    version 2.0;\n    format ascii;\n    class {cls};\n'
                f'    location "{f.parent.relative_to(case).as_posix()}";\n    object {f.name};\n}}\n\n')
        f.write_text(header+body)
    copy2(root/'geometry'/'naya_concept.stl',case/'constant'/'triSurface'/'naya_concept.stl')
    print('OpenFOAM starter case written to',case)
if __name__=='__main__':mk()
