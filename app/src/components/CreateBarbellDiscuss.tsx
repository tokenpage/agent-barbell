import React from 'react';

import { generateUUID } from '@kibalabs/core';
import { Alignment, Box, Direction, Stack, Text } from '@kibalabs/ui-react';

import { useAuth } from '../AuthContext';
import { CreateBarbellConfig, Resources } from '../client';
import { useGlobals } from '../GlobalsContext';
import { ChatView } from './ChatView';

interface CreateBarbellDiscussProps {
  config: CreateBarbellConfig;
}

const SUGGESTIONS = [
  'Why is SGOV the safe end?',
  'What does a 15% loss budget mean?',
  'How should I choose a stock satellite?',
];

export function CreateBarbellDiscuss(props: CreateBarbellDiscussProps): React.ReactElement {
  const { agentBarbellClient } = useGlobals();
  const { authToken } = useAuth();
  const conversationId = React.useRef<string>(generateUUID());
  const [messages, setMessages] = React.useState<Resources.ChatMessage[]>([]);
  const [isSending, setIsSending] = React.useState<boolean>(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const [isExpanded, setIsExpanded] = React.useState<boolean>(false);

  const sendMessage = async (content: string): Promise<void> => {
    const normalizedContent = content.trim();
    if (!normalizedContent || !authToken || isSending) {
      return;
    }
    setErrorMessage(null);
    setMessages((previousMessages: Resources.ChatMessage[]): Resources.ChatMessage[] => [
      ...previousMessages,
      new Resources.ChatMessage(generateUUID(), new Date(), normalizedContent, true),
    ]);
    setIsSending(true);
    try {
      await agentBarbellClient.addCreationMessageStreamed(
        conversationId.current,
        normalizedContent,
        props.config,
        authToken,
        (message: Resources.ChatMessage): void => {
          setMessages((previousMessages: Resources.ChatMessage[]): Resources.ChatMessage[] => [...previousMessages, message]);
        },
      );
    } catch (caughtError: unknown) {
      setErrorMessage(caughtError instanceof Error ? caughtError.message : 'The setup agent is unavailable right now.');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <Box className='ab-creation-discuss' variant='card' isFullWidth={true}>
      <button
        type='button'
        className='ab-creation-discuss-header'
        aria-expanded={isExpanded}
        aria-controls='creation-agent-chat'
        onClick={(): void => setIsExpanded((current: boolean): boolean => !current)}
      >
        <Stack direction={Direction.Horizontal} childAlignment={Alignment.Center} isFullWidth={true} shouldAddGutters={true}>
          <Stack.Item growthFactor={1} shrinkFactor={1}>
            <Stack direction={Direction.Vertical} childAlignment={Alignment.Start} shouldAddGutters={false}>
              <Text variant='bold'>Talk to the setup agent</Text>
              <Text variant='note'>Ask about the stock choices, loss budget, or strategy defaults.</Text>
            </Stack>
          </Stack.Item>
          <Text variant='note'>{isExpanded ? 'Hide' : 'Ask'}</Text>
        </Stack>
      </button>
      {isExpanded && (
        <Box id='creation-agent-chat' className='ab-creation-discuss-content' isFullWidth={true}>
          <ChatView
            messages={messages}
            isSending={isSending}
            errorMessage={errorMessage}
            onMessageSubmitted={sendMessage}
            suggestions={SUGGESTIONS}
            emptyStateText='Get a plain-language read on the draft before you create it.'
            inputPlaceholder='Ask about this barbell draft'
            isCompact={true}
          />
        </Box>
      )}
    </Box>
  );
}
