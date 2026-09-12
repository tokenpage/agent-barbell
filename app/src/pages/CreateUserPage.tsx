import React from 'react';

import { Alignment, Button, ContainingView, Direction, PaddingSize, SingleLineInput, Spacing, Stack, Text, TextAlignment } from '@kibalabs/ui-react';

import { useAuth } from '../AuthContext';

export function CreateUserPage(): React.ReactElement {
  const { createUser } = useAuth();
  const [username, setUsername] = React.useState('');
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const [isCreating, setIsCreating] = React.useState(false);

  const onCreateClicked = async (): Promise<void> => {
    setErrorMessage(null);
    setIsCreating(true);
    try {
      await createUser(username.trim().length > 0 ? username.trim() : null);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Failed to create user');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <ContainingView maxWidth='500px' className='ab-page'>
      <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} contentAlignment={Alignment.Center} shouldAddGutters={true} isFullHeight={true} isFullWidth={true} paddingVertical={PaddingSize.Wide2} paddingHorizontal={PaddingSize.Wide2}>
        <Text variant='header1' alignment={TextAlignment.Center}>Create your account</Text>
        <Text variant='note' alignment={TextAlignment.Center}>Your wallet is verified — pick an optional username to finish.</Text>
        <Spacing variant={PaddingSize.Wide} />
        <SingleLineInput value={username} onValueChanged={setUsername} placeholderText='Username (optional)' />
        {errorMessage && <Text variant='error'>{errorMessage}</Text>}
        <Button variant='primary' text={isCreating ? 'Creating...' : 'Create Account'} onClicked={onCreateClicked} isEnabled={!isCreating} />
      </Stack>
    </ContainingView>
  );
}
