#vertex
#version 420

layout(location = 0) in vec3 position;

out vec2 UV;
uniform mat4 vpMat;
uniform mat4 mMat;
uniform int flipud;
uniform int fliplr;

void main()
{
    gl_Position = vpMat * mMat * vec4(position, 1.0);
    UV = (vec2(position.x, position.y) + 1.0) / 2.0;
    if (flipud == 1)
        UV.y = 1.0 - UV.y;
    if (fliplr == 1)
        UV.x = 1.0 - UV.x;
}


#fragment 
#version 420

layout(location = 0) out vec4 fragmentColor;
layout(binding = 0) uniform usampler2D fbImage;

in vec2 UV;
uniform vec4 color;
uniform float contrast_min;
uniform float contrast_max;

void main()
{
    float fpixelValue = float(texture(fbImage, UV).r);
    fpixelValue = (fpixelValue - contrast_min) / (contrast_max - contrast_min);
    fragmentColor = fpixelValue * color;
    fragmentColor.a = 1.0;
}
