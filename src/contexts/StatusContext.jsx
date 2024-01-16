import React from 'react';
import PropTypes from 'prop-types';

export const StatusContext = React.createContext(null);

/**
 * Provider for the status context used to manage the status bar.
 *
 * @return {*} The component.
 */
export function StatusProvider({children}) {
  return <StatusContext.Provider value={{}}>{children}</StatusContext.Provider>;
}

StatusProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
