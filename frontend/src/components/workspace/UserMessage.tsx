interface UserMessageProps {
  content: string;
}

export function UserMessage({ content }: UserMessageProps) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[85%] rounded-2xl rounded-br-md bg-[#e8ebf0] px-4 py-3 text-[15px] leading-7 text-ink">
        {content}
      </div>
    </div>
  );
}
