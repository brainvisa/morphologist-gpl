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


// material
vec3 ambientMat = vec3(0.1, 0.1, 0.1);
vec3 specularMat = vec3(0.2, 0.2, 0.2);
vec3 diffuseMat = vertexColor.rgb;
float shininessMat = 3.;

// lighting
vec3 ambientLight = vec3(0., 0., 0.);
vec3 diffuseLight = vec3(1., 1., 1.);
vec3 specularLight = vec3(1., 1., 1.);
vec3 directionLight = normalize(vec3(0, 0, -1.0)); // defined in the eye space.


void main(void)
{
	// vertex
	vec4 eyeVertexPosition = viewMatrix * modelMatrix
				* vec4(vertexPosition, 1.0);
	gl_Position = perspectiveMatrix * eyeVertexPosition;

	//normal
	mat4 normalMatrix = viewMatrixIT * modelMatrixIT;
	vec3 transformedNormal = (normalMatrix * vec4(vertexNormal, 1.0)).xyz;
	transformedNormal = normalize(transformedNormal);

	// ambient
	vec3 ambientColor = ambientLight * ambientMat;

	// diffuse
	float cos_theta = max(dot(transformedNormal, -directionLight), 0.0);
	vec3 diffuseColor = diffuseLight * diffuseMat * cos_theta;

	// specular
	vec3 eyeDirection = normalize(-eyeVertexPosition.xyz);
	vec3 reflectionDirection = reflect(directionLight, transformedNormal);
	float cos_alpha = max(dot(reflectionDirection, eyeDirection), 0.0);
	float specularFactor = pow(cos_alpha, shininessMat);
	vec3 specularColor = specularLight * specularMat * specularFactor;

	fragmentColor = vec4(ambientColor + diffuseColor + specularColor, 1.0);
}
