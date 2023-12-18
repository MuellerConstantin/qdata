import React from 'react';
import BorderTemplate from '../components/templates/BorderTemplate';
import DataView from '../components/organisms/file/DataView';

/**
 * The landing page of the application.
 *
 * @return {*} The component
 */
export default function Home() {
  return (
    <BorderTemplate>
      <DataView />
    </BorderTemplate>
  );
}
