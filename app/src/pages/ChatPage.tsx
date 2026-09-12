import React from 'react';

import { Alignment, ContainingView, Direction, LoadingSpinner, PaddingSize, Stack, Text } from '@kibalabs/ui-react';
import { useQueryClient } from '@tanstack/react-query';

import { useAuth } from '../AuthContext';
import { useBarbell } from '../BarbellContext';
import { Resources } from '../client';
import { ChatView } from '../components/ChatView';
import { useGlobals } from '../GlobalsContext';

export function ChatPage(): React.ReactElement {
  const { agentBarbellClient } = useGlobals();
  const { authToken } = useAuth();
  const { barbell, refresh } = useBarbell();
  const queryClient = useQueryClient();
  const [messages, setMessages] = React.useState<Resources.ChatMessage[]>([]);
  const [isSending, setIsSending] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const barbellId = barbell?.barbellId;

  React.useEffect((): void => {
    if (barbellId == null || authToken == null) {
      return;
    }
    agentBarbellClient.listChatMessages(barbellId, authToken)
      .then(setMessages)
      .catch((error: Error): void => setErrorMessage(error.message));
  }, [agentBarbellClient, barbellId, authToken]);

  const onMessageSubmitted = React.useCallback(async (content: string): Promise<void> => {
    if (barbellId == null || authToken == null) {
      return;
    }
    setErrorMessage(null);
    setIsSending(true);
    try {
      await agentBarbellClient.addUserMessageStreamed(barbellId, content, authToken, (message: Resources.ChatMessage): void => {
        setMessages((currentMessages: Resources.ChatMessage[]): Resources.ChatMessage[] => [...currentMessages, message]);
      });
      // The agent may have changed the policy, so the overview's cached risk state is stale.
      queryClient.invalidateQueries({ queryKey: ['riskState', barbellId] });
      refresh();
    } catch (error: unknown) {
      setErrorMessage((error as Error).message);
    } finally {
      setIsSending(false);
    }
  }, [agentBarbellClient, barbellId, authToken, queryClient, refresh]);

  if (barbell == null) {
    return (
      <ContainingView maxWidth='640px' className='ab-page'>
        <Stack direction={Direction.Vertical} childAlignment={Alignment.Center} paddingVertical={PaddingSize.Wide2}>
          <LoadingSpinner />
        </Stack>
      </ContainingView>
    );
  }

  return (
    <ContainingView maxWidth='640px' className='ab-page'>
      <Stack direction={Direction.Vertical} isFullWidth={true} isFullHeight={true} shouldAddGutters={true} paddingVertical={PaddingSize.Wide2} paddingHorizontal={PaddingSize.Wide2}>
        <Text variant='header2'>Talk to your agent</Text>
        <Text variant='note'>The agent sets bounds. A deterministic engine decides position sizes inside them, and only you can clear a fired kill switch.</Text>
        <ChatView messages={messages} isSending={isSending} errorMessage={errorMessage} onMessageSubmitted={onMessageSubmitted} />
      </Stack>
    </ContainingView>
  );
}
