import * as React from "react"
import { Upload, X, File } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

const FileUpload = React.forwardRef(({ 
  className, 
  accept, 
  onChange, 
  value, 
  label,
  required = false,
  ...props 
}, ref) => {
  const [isDragging, setIsDragging] = React.useState(false)
  const fileInputRef = React.useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleFileSelect = (file) => {
    if (file && onChange) {
      // Create a FileList-like object
      const dataTransfer = new DataTransfer()
      dataTransfer.items.add(file)
      const fakeEvent = {
        target: {
          files: dataTransfer.files
        }
      }
      onChange(fakeEvent)
    }
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const handleRemove = (e) => {
    e.stopPropagation()
    if (onChange) {
      onChange({ target: { files: [] } })
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const file = value || (fileInputRef.current?.files?.[0])

  return (
    <div className={cn("space-y-2", className)}>
      <input
        ref={(node) => {
          fileInputRef.current = node
          if (typeof ref === 'function') ref(node)
          else if (ref) ref.current = node
        }}
        type="file"
        accept={accept}
        onChange={onChange}
        className="hidden"
        required={required}
        {...props}
      />
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        className={cn(
          "relative border-2 border-dashed rounded-lg p-6 transition-colors cursor-pointer",
          isDragging
            ? "border-primary bg-primary/5"
            : file
            ? "border-green-300 bg-green-50/50"
            : "border-gray-300 hover:border-gray-400 hover:bg-gray-50/50"
        )}
      >
        {file ? (
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3 flex-1 min-w-0">
              <div className="flex-shrink-0 p-2 bg-green-100 rounded-lg">
                <File className="h-5 w-5 text-green-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {file.name}
                </p>
                <p className="text-xs text-gray-500">
                  {(file.size / 1024).toFixed(2)} KB
                </p>
              </div>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleRemove}
              className="flex-shrink-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center text-center">
            <div className="p-3 bg-gray-100 rounded-full mb-3">
              <Upload className="h-6 w-6 text-gray-600" />
            </div>
            <p className="text-sm font-medium text-gray-700 mb-1">
              Click to upload or drag and drop
            </p>
            <p className="text-xs text-gray-500">
              {accept ? `Accepted: ${accept.replace(/\./g, '').replace(/,/g, ', ')}` : 'Any file'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
})
FileUpload.displayName = "FileUpload"

export { FileUpload }
