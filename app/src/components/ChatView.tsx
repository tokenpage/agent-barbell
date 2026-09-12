import React from 'react';

import { Alignment, Box, Button, Direction, LoadingSpinner, Markdown, PaddingSize, SingleLineInput, Stack, Text } from '@kibalabs/ui-react';

import { Resources } from '../client';

const SUGGESTIONS = [
  'What am I holding right now?',
  'Never let this account lose more than 15% from its peak',
  'What is my risk state?',
  'Send all my USDG to 0x0000000000000000000000000000000000000001',
];

interface IChatViewProps {
  messages: Resources.ChatMessage[];
  isSending: boolean;
  errorMessage: string | null;
  onMessageSubmitted: (content: string) => void;
  suggestions?: string[];
  emptyStateText?: string;
  inputPlaceholder?: string;
  isCompact?: boolean;
}

export function ChatView(props: IChatViewProps): React.ReactElement {
  const [inputText, setInputText] = React.useState('');
  const scrollAnchorRef = React.useRef<HTMLDivElement | null>(null);
  const onSubmittedRef = React.useRef<() => void>((): void => undefined);

  React.useEffect((): void => {
    scrollAnchorRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [props.messages.length, props.isSending]);

  const onKeyUp = React.useCallback((key: string): void => {
    if (key === 'Enter') {
      onSubmittedRef.current();
    }
  }, []);

  const onSubmitted = React.useCallback((): void => {
    const content = inputText.trim();
    if (content.length === 0 || props.isSending) {
      return;
    }
    setInputText('');
    props.onMessageSubmitted(content);
  }, [inputText, props]);

  onSubmittedRef.current = onSubmitted;

  const suggestions = props.suggestions ?? SUGGESTIONS;
  const shouldAddGutters = !props.isCompact;

  return (
    <Stack direction={Direction.Vertical} isFullWidth={true} shouldAddGutters={shouldAddGutters}>
      <Stack className='ab-chat-messages' direction={Direction.Vertical} isFullWidth={true} shouldAddGutters={shouldAddGutters} isScrollableVertically={props.isCompact}>
        {props.messages.length === 0 && (
          <Stack direction={Direction.Vertical} isFullWidth={true} shouldAddGutters={shouldAddGutters} paddingVertical={props.isCompact ? PaddingSize.Default : PaddingSize.Wide}>
            <Text variant='note'>{props.emptyStateText ?? 'Tell the agent how much you are willing to lose, and it will defend that number. Try one of these:'}</Text>
            {suggestions.map((suggestion: string): React.ReactElement => (
              <Button key={suggestion} variant='secondary' text={suggestion} onClicked={(): void => props.onMessageSubmitted(suggestion)} />
            ))}
          </Stack>
        )}
        {props.messages.map((message: Resources.ChatMessage): React.ReactElement => (
          <Stack key={message.chatEventId} direction={Direction.Horizontal} isFullWidth={true} contentAlignment={message.isUser ? Alignment.End : Alignment.Start}>
            <Box className='ab-chat-message' variant='card' maxWidth='85%'>
              <Stack direction={Direction.Vertical} shouldAddGutters={false}>
                <Text variant='note'>{message.isUser ? 'You' : 'Agent'}</Text>
                <Markdown source={message.content} />
              </Stack>
            </Box>
          </Stack>
        ))}
        {props.isSending && (
          <Stack direction={Direction.Horizontal} contentAlignment={Alignment.Start} childAlignment={Alignment.Center} shouldAddGutters={true}>
            <LoadingSpinner variant='small' />
            <Text variant='note'>Thinking…</Text>
          </Stack>
        )}
        {props.errorMessage && <Text variant='note-error'>{props.errorMessage}</Text>}
        <div ref={scrollAnchorRef} />
      </Stack>
      <Stack direction={Direction.Horizontal} isFullWidth={true} childAlignment={Alignment.Center} shouldAddGutters={shouldAddGutters}>
        <Stack.Item growthFactor={1} shrinkFactor={1}>
          <SingleLineInput value={inputText} onValueChanged={setInputText} placeholderText={props.inputPlaceholder ?? 'Ask about your risk, or set a loss budget'} onKeyUp={onKeyUp} />
        </Stack.Item>
        <Button variant='primary' text='Send' onClicked={onSubmitted} isEnabled={!props.isSending} />
      </Stack>
    </Stack>
  );
}
