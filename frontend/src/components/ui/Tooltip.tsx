import * as TooltipPrimitive from '@radix-ui/react-tooltip'
import React from 'react'

interface TooltipProps {
  content: React.ReactNode
  children: React.ReactElement
  link?: string
  linkLabel?: string
}

export function Tooltip({ content, children, link, linkLabel }: TooltipProps) {
  return (
    <TooltipPrimitive.Provider delayDuration={300}>
      <TooltipPrimitive.Root>
        <TooltipPrimitive.Trigger asChild>{children}</TooltipPrimitive.Trigger>
        <TooltipPrimitive.Portal>
          <TooltipPrimitive.Content
            className="z-50 max-w-xs rounded-lg bg-gray-900 px-3 py-2 text-xs text-white shadow-xl animate-in fade-in-0 zoom-in-95"
            sideOffset={6}
          >
            <p>{content}</p>
            {link && (
              <a
                href={link}
                target="_blank"
                rel="noreferrer"
                className="mt-1 block text-blue-300 underline hover:text-blue-200"
              >
                {linkLabel ?? 'Referência'}
              </a>
            )}
            <TooltipPrimitive.Arrow className="fill-gray-900" />
          </TooltipPrimitive.Content>
        </TooltipPrimitive.Portal>
      </TooltipPrimitive.Root>
    </TooltipPrimitive.Provider>
  )
}
