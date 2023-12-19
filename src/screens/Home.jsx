import React from 'react';
import BorderTemplate from '../components/templates/BorderTemplate';
import FileExplorer from '../components/organisms/file/FileExplorer';

/**
 * The landing page of the application.
 *
 * @return {*} The component
 */
export default function Home() {
  return (
    <BorderTemplate>
      <FileExplorer />
    </BorderTemplate>
  );
}
