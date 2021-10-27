#version 120
uniform sampler2D u_modelTexture;
uniform sampler2D u_shadowMap;
varying vec4 v_shadowCoord;

void main()                                                                         
{
    vec3 projCoords = v_shadowCoord.xyz/v_shadowCoord.w;
    float closestDepth = texture2D(u_shadowMap, projCoords.xy).r;
    float currentDepth = projCoords.z;  
    float shadow = currentDepth > closestDepth  ? 1.0 : 0.0;
    gl_FragColor = shadow * texture2D(u_modelTexture, gl_TexCoord[0].xy);
}