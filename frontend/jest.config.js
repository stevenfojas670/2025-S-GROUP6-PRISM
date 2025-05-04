const nextJest = require('next/jest');

const createJestConfig = nextJest({ dir: './' }); // Assumes you're in frontend/

const customJestConfig = {
	setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
	testEnvironment: 'jsdom',
	moduleNameMapper: {
		'^@/(.*)$': '<rootDir>/src/$1', // ✅ matches tsconfig path
	},
	transform: {
		'^.+\\.(js|jsx|ts|tsx)$': ['babel-jest', { presets: ['next/babel'] }],
	},
};

module.exports = createJestConfig(customJestConfig);
