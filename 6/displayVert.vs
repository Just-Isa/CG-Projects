#version 120

uniform mat4 u_biasMVPMatrix;
varying vec4 v_shadowCoord;

void main()
{
    mat4 bias = mat4(0.5, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.5, 0.5, 0.5, 1.0);
    gl_Position = gl_ProjectionMatrix * gl_ModelViewMatrix * gl_Vertex;
    v_shadowCoord = u_biasMVPMatrix * gl_Vertex;
    gl_TexCoord[0] = gl_MultiTexCoord0;
}