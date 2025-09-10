import React, { useState, useRef } from 'react'
import { PenTool, Upload, Camera, Languages, Copy, CheckCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Select from '@/components/ui/Select'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { aiService } from '@/utils/api'
import { Language, HandwritingResult } from '@/types'
import { parseItemName } from '@/utils/helpers'
import toast from 'react-hot-toast'

const HandwritingRecognition: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string>('')
  const [language, setLanguage] = useState<Language>('auto')
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<HandwritingResult | null>(null)
  const [copiedText, setCopiedText] = useState(false)
  
  const fileInputRef = useRef<HTMLInputElement>(null)

  const languageOptions = [
    { value: 'auto', label: 'Auto Detect' },
    { value: 'tamil', label: 'Tamil' },
    { value: 'english', label: 'English' },
    { value: 'mixed', label: 'Tamil + English' },
  ]

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (!file.type.startsWith('image/')) {
        toast.error('Please select an image file')
        return
      }
      
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        toast.error('File size must be less than 10MB')
        return
      }

      setSelectedFile(file)
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
      setResult(null)
    }
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const handleCameraClick = () => {
    // In a real app, this would open camera interface
    toast.info('Camera functionality would be implemented here')
  }

  const recognizeHandwriting = async () => {
    if (!selectedFile) {
      toast.error('Please select an image first')
      return
    }

    setIsProcessing(true)
    try {
      const result = await aiService.recognizeHandwriting(selectedFile, language)
      setResult(result)
      
      if (result.error) {
        toast.error(`Recognition failed: ${result.error}`)
      } else {
        toast.success(`Text recognized with ${(result.confidence * 100).toFixed(1)}% confidence`)
      }
    } catch (error) {
      console.error('Handwriting recognition failed:', error)
      toast.error('Failed to recognize handwriting')
    } finally {
      setIsProcessing(false)
    }
  }

  const copyToClipboard = async () => {
    if (result?.text) {
      try {
        await navigator.clipboard.writeText(result.text)
        setCopiedText(true)
        toast.success('Text copied to clipboard')
        setTimeout(() => setCopiedText(false), 2000)
      } catch (error) {
        toast.error('Failed to copy text')
      }
    }
  }

  const useRecognizedText = () => {
    if (result?.text) {
      const parsed = parseItemName(result.text)
      toast.success(`Parsed: ${parsed.name}${parsed.quantity ? ` (Qty: ${parsed.quantity})` : ''}`)
      // In a real app, this would navigate to bill generator and populate the form
    }
  }

  const translateText = async () => {
    if (!result?.text) return

    try {
      const sourceLang = result.languageDetected === 'tamil' ? 'tamil' : 'english'
      const targetLang = sourceLang === 'tamil' ? 'english' : 'tamil'
      
      const translation = await aiService.translateText(result.text, sourceLang, targetLang)
      toast.success(`Translation: ${translation.translatedText}`)
    } catch (error) {
      toast.error('Translation failed')
    }
  }

  const clearAll = () => {
    setSelectedFile(null)
    setPreviewUrl('')
    setResult(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <PenTool className="h-6 w-6" />
        <h1 className="text-2xl font-bold text-gray-900">Handwriting Recognition</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle>Upload Image</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            <div className="flex gap-2">
              <Button
                onClick={handleUploadClick}
                variant="secondary"
                className="flex items-center gap-2"
              >
                <Upload className="h-4 w-4" />
                Select Image
              </Button>
              
              <Button
                onClick={handleCameraClick}
                variant="secondary"
                className="flex items-center gap-2"
              >
                <Camera className="h-4 w-4" />
                Take Photo
              </Button>
            </div>

            {previewUrl && (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="max-w-full h-auto max-h-64 mx-auto rounded"
                />
                <p className="text-sm text-gray-500 mt-2 text-center">
                  {selectedFile?.name}
                </p>
              </div>
            )}

            <Select
              label="Language"
              options={languageOptions}
              value={language}
              onChange={(e) => setLanguage(e.target.value as Language)}
            />

            <div className="flex gap-2">
              <Button
                onClick={recognizeHandwriting}
                disabled={!selectedFile || isProcessing}
                loading={isProcessing}
                className="flex-1"
              >
                {isProcessing ? 'Processing...' : 'Recognize Handwriting'}
              </Button>
              
              <Button
                onClick={clearAll}
                variant="secondary"
                disabled={!selectedFile}
              >
                Clear
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Results Section */}
        <Card>
          <CardHeader>
            <CardTitle>Recognition Results</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {isProcessing && (
              <div className="flex items-center justify-center py-8">
                <LoadingSpinner size="lg" />
                <span className="ml-3 text-gray-600">Analyzing handwriting...</span>
              </div>
            )}

            {result && !isProcessing && (
              <>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <label className="text-sm font-medium text-gray-700">Recognized Text:</label>
                  <p className="text-lg font-medium mt-1">{result.text}</p>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Confidence:</span>
                    <span className="ml-2">{(result.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div>
                    <span className="font-medium">Language:</span>
                    <span className="ml-2 capitalize">{result.languageDetected}</span>
                  </div>
                </div>

                {result.words && result.words.length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Word Details:</label>
                    <div className="mt-2 space-y-1">
                      {result.words.map((word, index) => (
                        <div key={index} className="flex justify-between text-sm">
                          <span>{word.text}</span>
                          <span className="text-gray-500">{(word.confidence * 100).toFixed(1)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex gap-2">
                  <Button
                    onClick={copyToClipboard}
                    variant="secondary"
                    size="sm"
                    className="flex items-center gap-2"
                  >
                    {copiedText ? (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                    {copiedText ? 'Copied!' : 'Copy Text'}
                  </Button>

                  <Button
                    onClick={translateText}
                    variant="secondary"
                    size="sm"
                    className="flex items-center gap-2"
                  >
                    <Languages className="h-4 w-4" />
                    Translate
                  </Button>

                  <Button
                    onClick={useRecognizedText}
                    size="sm"
                    className="flex items-center gap-2"
                  >
                    <CheckCircle className="h-4 w-4" />
                    Use This Text
                  </Button>
                </div>
              </>
            )}

            {!result && !isProcessing && (
              <div className="text-center py-8 text-gray-500">
                Upload an image and click "Recognize Handwriting" to see results here.
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Tips Section */}
      <Card>
        <CardHeader>
          <CardTitle>Tips for Better Recognition</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-gray-600">
            <li>• Ensure good lighting and clear image quality</li>
            <li>• Write clearly with sufficient spacing between words</li>
            <li>• Avoid shadows or reflections on the text</li>
            <li>• For Tamil text, use standard script forms</li>
            <li>• Keep the image orientation correct (not rotated)</li>
            <li>• Supported formats: JPG, PNG, TIFF, BMP</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}

export default HandwritingRecognition