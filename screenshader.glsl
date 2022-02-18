#vertex
#version 420

layout(location = 0) in vec3 position;

out vec2 UV;
uniform mat4 vp_mat;

void main()
{
    gl_Position = vp_mat * vec4(position, 1.0);
    UV = (vec2(position.x, position.y) + 1.0) / 2.0;
}


#fragment 
#version 420

layout(location = 0) out vec4 fragmentColor;
layout(binding = 0) uniform sampler2D fbImage;

in vec2 UV;

void main()
{
    fragmentColor = texture(fbImage, UV);
    fragmentColor.a = 1.0;
    fragmentColor = vec4(UV.x, UV.y, 1.0, 1.0);
}
