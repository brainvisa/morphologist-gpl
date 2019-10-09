#ifdef GL_ES
precision highp float;
#endif
varying vec4 fragmentColor;
varying vec3 transformedNormal;
varying vec4 eyeVertexPosition;

// material
vec3 ambientMat = vec3(0.1, 0.1, 0.1);
vec3 specularMat = vec3(0.2, 0.2, 0.2);
vec3 diffuseMat = vec3(0.1, 0.1, 0.1); //fragmentColor.rgb;
float shininessMat = 3.;

// lighting
vec3 ambientLight = vec3(0., 0., 0.);
vec3 diffuseLight = vec3(1., 1., 1.);
vec3 specularLight = vec3(1., 1., 1.);
vec3 directionLight = normalize(vec3(0, 0, -1.0)); // defined in the eye space.

void main(void)
{
        diffuseMat = fragmentColor.rgb;
	// normal
	vec3 normal = normalize(transformedNormal);

	// ambient
	vec3 ambientColor = ambientLight * ambientMat;

	// diffuse
	float cos_theta = max(dot(normal, -directionLight), 0.0);
	vec3 diffuseColor = diffuseLight * diffuseMat * cos_theta;

	// specular (Blinn-Phong model)
	vec3 eyeDirection = normalize(-eyeVertexPosition.xyz);
	vec3 reflectionDirection = reflect(directionLight, normal);
	float cos_alpha = max(dot(reflectionDirection, eyeDirection), 0.0);
	float specularFactor = pow(cos_alpha, shininessMat);
	vec3 specularColor = specularLight * specularMat * specularFactor;


	gl_FragColor = vec4(ambientColor + diffuseColor + specularColor, 1.0);
}
