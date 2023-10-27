#version 330

#if defined VERTEX_SHADER

in vec2 in_vert;
out vec2 v_text;

void main()
{
    gl_Position = vec4(in_vert, 0.0, 1.0);
	v_text = in_vert;
}


#elif defined FRAGMENT_SHADER

#ifdef GL_ES
precision mediump float;
#endif



uniform vec2    u_resolution;
uniform float   u_time;
uniform float   u_size;
uniform float   u_bright;
uniform float   u_cutoff;
uniform int   	u_noisetype;

out vec4 f_color;

#include lygia/generative/random.glsl
#include lygia/generative/cnoise.glsl
#include lygia/generative/worley.glsl
#include lygia/generative/curl.glsl
#include lygia/generative/fbm.glsl
#include lygia/generative/gnoise.glsl
#include lygia/generative/noised.glsl
#include lygia/generative/snoise.glsl
#include lygia/generative/voronoi.glsl
#include lygia/generative/voronoise.glsl

float hash12(vec2 p)
{
	vec3 p3  = fract(vec3(p.xyx) * .1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

vec3 hash33(vec3 p3)
{
	p3 = fract(p3 * vec3(.1031, .1030, .0973));
    p3 += dot(p3, p3.yxz+33.33);
    return fract((p3.xxy + p3.yxx)*p3.zyx);

}

#define ITERATIONS 1
vec4 noise(vec2 position)
{
	//vec2 position = gl_FragCoord.xy;
    // vec2 uv = gl_FragCoord.xy / u_resolution.xy;
#if 0
	float a = 0.0;
    for (int t = 0; t < ITERATIONS; t++)
    {
        float v = float(t+1)*.152;
        vec2 pos = (position * v + u_time * 1500. + 50.0);
        a += hash12(pos.xy);
    }
    vec3 col = vec3(a) / float(ITERATIONS);
#else
	vec3 a = vec3(0.0);
    for (int t = 0; t < ITERATIONS; t++)
    {
        float v = float(t+1)*.132;
        vec3 pos = vec3(position, u_time*.3) + u_time * 500. + 50.0;
        a += hash33(pos);
    }
    vec3 col = a / float(ITERATIONS);
#endif

    
	return vec4(col, 1.0);
}


void main(void) {
	vec2 scaled_pos =  floor(gl_FragCoord.xy/u_size);
	vec4 color = vec4(vec3(0.0), 1.0);
	vec2 pixel = u_size/u_resolution.xy;
	vec2 st = gl_FragCoord.xy * pixel;
	vec2 p = vec2(0.0);
	float r = 0;
	
	switch(u_noisetype){
	case 0:
		// Hash function noise
		color += noise(scaled_pos);
		color = step(u_cutoff,color)*(color-u_cutoff)/(1.0-u_cutoff);
		f_color = color*u_bright;
		break;
	case 1:
		// random noise 
		r = random(vec3(st * 5., u_time));
		color += vec4(step(u_cutoff,r)*(r-u_cutoff)/(1.0-u_cutoff));

		f_color = color*u_bright;

		break;
	case 2:
		r = cnoise(vec3(st * 5.,u_time)) * 0.5 + 0.5;
		color += vec4(step(u_cutoff,r)*(r-u_cutoff)/(1.0-u_cutoff));

		f_color = color*u_bright;
		break;
	case 3:
		r = worley(vec3(st*10., u_time));
		color += vec4(step(u_cutoff,r)*(r-u_cutoff)/(1.0-u_cutoff));
		f_color = color*u_bright;
		break;
	case 4:
		color.rgb += curl(vec3(st * 5.,u_time)) * 0.5 + 0.5;
		color = step(u_cutoff,color)*(color-u_cutoff)/(1.0-u_cutoff);

		f_color = color*u_bright;
		break;
	case 5:
		r = fbm(vec3(st * 5.,u_time)) * 0.5 + 0.5;
		color += vec4(step(u_cutoff,r)*(r-u_cutoff)/(1.0-u_cutoff));

		f_color = color*u_bright;
		break;
	case 6:
		r = gnoise(vec3(st * 5.,u_time)) * 0.5 + 0.5;
		color += vec4(step(u_cutoff,r)*(r-u_cutoff)/(1.0-u_cutoff));

		f_color = color*u_bright;
		break;		
	case 7:
		color.rgb += noised(vec3(st * 5.,u_time)).yzw * 0.5 + 0.5;
		color = step(u_cutoff,color)*(color-u_cutoff)/(1.0-u_cutoff);

		f_color = color*u_bright;
		break;	
	break;
	case 8:
		r = snoise(vec3(st * 5.,u_time)) * 0.5 + 0.5;
		color += vec4(step(u_cutoff,r)*(r-u_cutoff)/(1.0-u_cutoff));

		f_color = color*u_bright;	
	break;
	case 9:
		color.rgb += voronoi(vec3(st * 5.,u_time)) * 0.5 + 0.5;
		color = step(u_cutoff,color)*(color-u_cutoff)/(1.0-u_cutoff);

		f_color = color*u_bright;
		break;	
	case 10:
		p = 0.5 - 0.5*cos( u_time * vec2(1.0,0.5) );
		p = p*p*(3.0-2.0*p);
		p = p*p*(3.0-2.0*p);
		p = p*p*(3.0-2.0*p);
		color += voronoise(vec3(24.0*st, u_time), p.x, 1.0 );
		color = step(u_cutoff,color)*(color-u_cutoff)/(1.0-u_cutoff);

		f_color = color*u_bright;
		break;
	default:
		f_color = noise(scaled_pos)*u_bright;
		break;
	}
		
}

#endif