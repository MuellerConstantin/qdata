import React from 'react';
import PropTypes from 'prop-types';

/**
 * The default window template. Organizes the window into header, main, and footer.
 *
 * @return {*} The component
 */
export default function BorderTemplate({children}) {
  return (
    <div className="h-full flex flex-col">
      <header />
      <main className="grow">{children}</main>
      <footer />
    </div>
  );
}

BorderTemplate.propTypes = {
  children: PropTypes.node,
};
