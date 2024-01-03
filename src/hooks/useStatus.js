import {useContext} from 'react';
import {StatusContext} from '../contexts/StatusContext';

/**
 * Hook to listen to status events and update the status.
 *
 * @return {object} Returns the context properties.
 */
export default function useStatus() {
  const context = useContext(StatusContext);

  if (!context) {
    throw new Error('useStatus() may be used only in the context of a <StatusProvider> component.');
  }

  return context;
}
