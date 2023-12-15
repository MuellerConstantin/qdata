import React, {forwardRef} from 'react';
import PropTypes from 'prop-types';

/**
 * Default button component.
 *
 * @return {JSX.Element} Button component
 */
const Button = forwardRef(({className, children, ...props}, ref) => (
  <button
    ref={ref}
    type="button"
    className={
      'group relative py-1 px-2 text-sm font-medium rounded outline-none bg-white ' +
      'border border-slate-300 text-slate-800 disabled:cursor-not-allowed ' +
      `focus:outline-slate-100 hover:brightness-95 disabled:brightness-75 hover:cursor-pointer ${className}`
    }
    {...props}
  >
    {children}
  </button>
));

Button.displayName = 'Button';

Button.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
};

export default Button;
