import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Save, RefreshCw, Users, Shield } from 'lucide-react'

// Define all available pages
const ALL_PAGES = [
  { id: 'change-requests', name: 'Change Requests', description: 'Create and manage change requests' },
  { id: 'publish', name: 'Publish Changes', description: 'Publish changes to bank endpoints' },
  { id: 'status', name: 'Status Center', description: 'View publication status' },
  { id: 'bank-monitoring', name: 'Bank Monitoring', description: 'Monitor bank status' },
]

export default function AccessManagementTab() {
  // State for Product role access
  const [productAccess, setProductAccess] = useState({
    'change-requests': true,
    'publish': true,
    'status': true,
    'bank-monitoring': true,
  })

  // State for Developer role access
  const [developerAccess, setDeveloperAccess] = useState({
    'change-requests': true,
    'publish': false,
    'status': false,
    'bank-monitoring': false,
  })

  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(false)

  // Load access settings on mount
  useEffect(() => {
    loadAccessSettings()
  }, [])

  const loadAccessSettings = async () => {
    setLoading(true)
    try {
      // TODO: Load from API
      // For now, using default values set in useState
      // In production, fetch from backend:
      // const response = await accessAPI.getRoleAccess()
      // setProductAccess(response.data.product)
      // setDeveloperAccess(response.data.developer)
    } catch (error) {
      console.error('Error loading access settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleProductAccessChange = (pageId, enabled) => {
    setProductAccess(prev => ({
      ...prev,
      [pageId]: enabled
    }))
  }

  const handleDeveloperAccessChange = (pageId, enabled) => {
    setDeveloperAccess(prev => ({
      ...prev,
      [pageId]: enabled
    }))
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      // TODO: Save to API
      // await accessAPI.updateRoleAccess({
      //   product: productAccess,
      //   developer: developerAccess
      // })
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      alert('Access settings saved successfully!')
    } catch (error) {
      console.error('Error saving access settings:', error)
      alert('Failed to save access settings. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    if (confirm('Are you sure you want to reset to default settings?')) {
      setProductAccess({
        'change-requests': true,
        'publish': true,
        'status': true,
        'bank-monitoring': true,
      })
      setDeveloperAccess({
        'change-requests': true,
        'publish': false,
        'status': false,
        'bank-monitoring': false,
      })
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Role Access Management
            </CardTitle>
            <CardDescription>
              Manage page access permissions for Product and Developer roles
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={loadAccessSettings}
              disabled={loading}
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button
              variant="outline"
              onClick={handleReset}
              disabled={saving || loading}
            >
              Reset
            </Button>
            <Button
              onClick={handleSave}
              disabled={saving || loading}
            >
              <Save className="mr-2 h-4 w-4" />
              {saving ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
            <span className="ml-2 text-gray-600">Loading access settings...</span>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Product Role Access - Left Side */}
            <Card className="border-2">
              <CardHeader className="bg-[#2F888A]/10 border-b">
                <CardTitle className="flex items-center gap-2 text-[#2F888A]">
                  <Users className="h-5 w-5" />
                  Product Role
                </CardTitle>
                <CardDescription>
                  Manage page access for Product team members
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <div className="space-y-4">
                  {ALL_PAGES.map((page) => (
                    <div
                      key={page.id}
                      className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <Checkbox
                        id={`product-${page.id}`}
                        checked={productAccess[page.id]}
                        onCheckedChange={(checked) =>
                          handleProductAccessChange(page.id, checked)
                        }
                        className="mt-1"
                      />
                      <div className="flex-1">
                        <Label
                          htmlFor={`product-${page.id}`}
                          className="text-sm font-medium cursor-pointer"
                        >
                          {page.name}
                        </Label>
                        <p className="text-xs text-gray-500 mt-1">
                          {page.description}
                        </p>
                      </div>
                      <div className="flex items-center">
                        {productAccess[page.id] ? (
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                            Enabled
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-full">
                            Disabled
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Developer Role Access - Right Side */}
            <Card className="border-2">
              <CardHeader className="bg-purple-50 border-b">
                <CardTitle className="flex items-center gap-2 text-purple-900">
                  <Users className="h-5 w-5" />
                  Developer Role
                </CardTitle>
                <CardDescription>
                  Manage page access for Developer team members
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <div className="space-y-4">
                  {ALL_PAGES.map((page) => (
                    <div
                      key={page.id}
                      className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <Checkbox
                        id={`developer-${page.id}`}
                        checked={developerAccess[page.id]}
                        onCheckedChange={(checked) =>
                          handleDeveloperAccessChange(page.id, checked)
                        }
                        className="mt-1"
                      />
                      <div className="flex-1">
                        <Label
                          htmlFor={`developer-${page.id}`}
                          className="text-sm font-medium cursor-pointer"
                        >
                          {page.name}
                        </Label>
                        <p className="text-xs text-gray-500 mt-1">
                          {page.description}
                        </p>
                      </div>
                      <div className="flex items-center">
                        {developerAccess[page.id] ? (
                          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                            Enabled
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-full">
                            Disabled
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
