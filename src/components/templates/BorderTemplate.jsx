import React from 'react';
import PropTypes from 'prop-types';

/**
 * The default window template. Organizes the window into header, main, and footer.
 *
 * @return {*} The component
 */
export default function BorderTemplate({children, header, footer}) {
  return (
    <div className="h-full flex flex-col">
      {header && <header>{header}</header>}
      <main className="grow">{children}</main>
      {footer && <footer>{footer}</footer>}
    </div>
  );
}

BorderTemplate.propTypes = {
  children: PropTypes.node,
  header: PropTypes.node,
  footer: PropTypes.node,
};
