#vertex
#version 420

layout(location = 0) in vec3 position;
out vec2 UV;

void main()
{
    gl_Position = vec4(position, 1.0);
    UV = (vec2(position.x, position.y) + 1.0) / 2.0;
}

#fragment
#version 420

layout (binding = 0) uniform usampler2D channelImage;
layout (binding = 1) uniform sampler2D fbImage;

in vec2 UV;
out vec4 fragmentColor;

uniform vec3 channel_color;
uniform float constrast_min;
uniform float constrast_max;

void main()
{
    vec4 framebufferColor = texture(fbImage, UV);
    float grayScale = float(texture(channelImage, UV).r);
    float contrast = (grayScale - constrast_min) / (constrast_max - constrast_min);
    contrast = max(0.0, contrast);
    vec3 pixelColor = contrast * channel_color;
    fragmentColor = framebufferColor + vec4(pixelColor, 1.0);
    fragmentColor.a = 1.0;
}
