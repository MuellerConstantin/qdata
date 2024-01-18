import React, {useState} from 'react';
import PropTypes from 'prop-types';

export const StatusContext = React.createContext(null);

/**
 * Provider for the status context used to manage the status bar.
 *
 * @return {*} The component.
 */
export function StatusProvider({children}) {
  const [loading, setLoading] = useState(false);
  const [filtered, setFiltered] = useState(false);
  const [totalRows, setTotalRows] = useState(null);
  const [totalColumns, setTotalColumns] = useState(null);

  return (
    <StatusContext.Provider
      value={{
        loading,
        setLoading,
        filtered,
        setFiltered,
        totalRows,
        setTotalRows,
        totalColumns,
        setTotalColumns,
      }}
    >
      {children}
    </StatusContext.Provider>
  );
}

StatusProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
