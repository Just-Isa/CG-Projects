#version 120                                                     

void main()                                                                         
{
    float z = gl_FragCoord.z;
    float n = 1.0;
    float f = 1000.0;
    //convert to linear values   
    //formula can be found at www.roxlu.com/2014/036/rendering-the-depth-buffer 
    float c = (2.0 * n) / (f + n - z * (f - n));                             
    gl_FragDepth = c;          
}