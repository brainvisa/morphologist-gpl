#ifdef GL_ES
precision highp float;
#endif

attribute vec3 vertexPosition;
attribute vec4 vertexColor;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 perspectiveMatrix;

varying vec4 fragmentColor;

void main(void)
{
	gl_Position = perspectiveMatrix * viewMatrix * modelMatrix
				* vec4(vertexPosition, 1.0);
	fragmentColor = vertexColor;
}
