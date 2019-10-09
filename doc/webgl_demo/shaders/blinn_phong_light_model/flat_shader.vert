#ifdef GL_ES
precision highp float;
#endif

attribute vec3 vertexPosition;
attribute vec4 vertexColor;
attribute vec3 vertexNormal;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 modelMatrixIT; // inversed then transposed
uniform mat4 viewMatrixIT;  // inversed then transposed
uniform mat4 perspectiveMatrix;

varying vec4 fragmentColor;
varying vec3 transformedNormal;
varying vec4 eyeVertexPosition;

void main(void)
{
	// vertex
	eyeVertexPosition = viewMatrix * modelMatrix
				* vec4(vertexPosition, 1.0);
	gl_Position = perspectiveMatrix * eyeVertexPosition;

	//normal
	mat4 normalMatrix = viewMatrixIT * modelMatrixIT;
	transformedNormal = (normalMatrix * vec4(vertexNormal, 1.0)).xyz;

	//color
	fragmentColor = vertexColor;
}
