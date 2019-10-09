#ifdef GL_ES
precision highp float;
#endif
varying vec4 fragmentColor;

void main(void)
{
	gl_FragColor = fragmentColor;
}
