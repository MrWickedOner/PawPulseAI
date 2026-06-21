import * as LocalAuthentication from 'expo-local-authentication';
import * as SecureStore from 'expo-secure-store';

export const isBiometricAvailable = async () => {
  const hasHardware = await LocalAuthentication.hasHardwareAsync();
  const isEnrolled = await LocalAuthentication.isEnrolledAsync();
  return hasHardware && isEnrolled;
};

export const authenticateWithBiometrics = async () => {
  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: 'Authenticate with biometrics',
    fallbackLabel: 'Use Password',
  });
  return result.success;
};

export const setBiometricsEnabled = async (enabled: boolean) => {
  await SecureStore.setItemAsync('biometricsEnabled', enabled ? 'true' : 'false');
};

export const getBiometricsEnabled = async () => {
  const enabled = await SecureStore.getItemAsync('biometricsEnabled');
  return enabled === 'true';
};
