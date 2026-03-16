import { useState, useEffect, useRef, Fragment } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { changeRequestAPI, setLocalChangeRequest, uploadArtifact, specGenerate, generateCrId3digit, listPartners, uploadManifest, broadcastManifest, sendManifestToPartner, getManifestDeliveryStatus, getManifestDownloadUrl, getOrchestratorStatus, getManifest } from '@/lib/api'
import { exportByChangeRequest, exportByPartner } from '@/lib/excelExport'

// Best party-reported status for a change (READY > TESTS_READY > TESTED > APPLIED > RECEIVED) for display in Partners tab
const PARTY_STATUS_ORDER = { READY: 5, TESTS_READY: 4, TESTED: 3, APPLIED: 2, RECEIVED: 1 }
function bestPartyStatusForChange(agentsMap) {
  if (!agentsMap || typeof agentsMap !== 'object') return null
  let best = null
  let bestRank = 0
  for (const status of Object.values(agentsMap)) {
    const rank = PARTY_STATUS_ORDER[status] ?? (status ? 0.5 : 0) // unknown status still shown
    if (rank > bestRank) {
      bestRank = rank
      best = status
    }
  }
  return best
}
import { parseXsdElementsAndAttributes, cn } from '@/lib/utils'
import { Upload, Send, Globe, FileText, CheckCircle2, Clock, XCircle, LogOut, User, RefreshCw, Search, Sparkles, FileCode, Copy, Check, ChevronDown, ChevronUp, Download, ScrollText } from 'lucide-react'
import { FileUpload } from '@/components/ui/file-upload'
import { useAuth } from '@/contexts/AuthContext'
import { useToast } from '@/contexts/ToastContext'
import DeveloperChangeRequestsTab from './DeveloperChangeRequestsTab'
import AccessManagementTab from './AccessManagementTab'
import DtoResultModal from './DtoResultModal'
import CodeComparisonModal from './CodeComparisonModal'
import changeIqBg from '@/assets/changeiq-login-bg.png'

const API_OPTIONS = [
  'ReqPay',
  'ReqRegMob',
  'ReqOtp',
  'ReqChkTxn',
  'ReqValAdd',
  'ReqBalEnq',
  'ReqBalChk'
]

const CHANGE_TYPES = [
  'Api Addition',
  'Element Addition',
  'Field Addition',
  'Field value changes'
]

const XSD_TYPE_OPTIONS = [
  'xs:string',
  'xs:integer',
  'xs:decimal',
  'xs:boolean',
  'xs:date',
  'xs:dateTime',
  'xs:token',
  'xs:positiveInteger',
  'xs:nonNegativeInteger',
  'xs:base64Binary',
  'xs:anyURI',
]

export default function AdminPortal() {
  const [activeTab, setActiveTab] = useState('change-requests')
  const { user, logout } = useAuth()
  const toast = useToast()

  const handleLogout = () => {
    logout()
    window.location.reload()
  }

  // Show tabs based on user role
  const showProductTabs = user === 'Product'
  const showDeveloperTabs = user === 'Developer'
  const showAdminTabs = user === 'Admin'

  // Theme: dark glass header/sidebar to suit background; role accent colors
  const themeProduct = user === 'Product'
  const themeDeveloper = user === 'Developer'
  const themeAdmin = user === 'Admin'
  const rootBgClass = 'min-h-screen'
  const headerBorderClass = themeProduct
    ? 'border-l-4 border-teal-300 pl-4'
    : themeDeveloper
      ? 'border-l-4 border-violet-400 pl-4'
      : themeAdmin
        ? 'border-l-4 border-violet-400 pl-4'
        : 'border-l-4 border-slate-400 pl-4'
  const titleClass = 'text-2xl sm:text-3xl font-bold text-white tracking-tight'
  const subtitleClass = 'text-slate-400 mt-1 text-sm'
  const dataTheme = user || 'default'

  // Left panel — Product & Developer: same base #2A4F61 (suits bg); different accent line/highlighter per role
  const sidebarAsideClass = themeProduct
    ? 'bg-[#2A4F61] rounded-r-2xl border-r border-white/15 border-l-4 border-l-teal-300 shadow-2xl'
    : themeDeveloper
      ? 'bg-[#2A4F61] rounded-r-2xl border-r border-white/15 border-l-4 border-l-violet-400 shadow-2xl'
      : themeAdmin
        ? 'bg-slate-800/85 backdrop-blur-xl rounded-r-2xl border-r border-white/10 border-l-4 border-l-violet-400 shadow-2xl'
        : 'bg-slate-800/80 backdrop-blur-xl rounded-r-2xl border border-white/10'
  const sidebarCardClass = 'sticky top-[104px] border-0 shadow-none bg-transparent'
  const hasSidebarTheme = themeProduct || themeDeveloper || themeAdmin
  const sidebarHeaderClass = (themeProduct || themeDeveloper) ? 'text-white font-semibold' : 'text-white font-semibold'
  const sidebarDescClass = themeProduct ? 'text-white/90 text-sm' : themeDeveloper ? 'text-white/90 text-sm' : 'text-slate-400 text-sm'
  const sidebarTabsClass = themeProduct
    ? 'flex h-auto w-full flex-col bg-transparent p-1.5 gap-1 [&_button]:text-white [&_button]:font-medium [&_button]:rounded-lg [&_button]:px-3 [&_button]:py-2.5 [&_button]:transition-colors [&_button:hover]:bg-teal-500/40 [&_button:hover]:text-white [&_button:focus-visible]:outline-none [&_button:focus-visible]:ring-2 [&_button:focus-visible]:ring-teal-200 [&_button:focus-visible]:ring-offset-2 [&_button:focus-visible]:ring-offset-[#2A4F61] [&_button[data-state=active]]:bg-teal-400/50 [&_button[data-state=active]]:text-white [&_button[data-state=active]]:border-l-4 [&_button[data-state=active]]:border-teal-200 [&_button[data-state=active]]:shadow-sm'
    : themeDeveloper
      ? 'flex h-auto w-full flex-col bg-transparent p-1.5 gap-1 [&_button]:text-white [&_button]:font-medium [&_button]:rounded-lg [&_button]:px-3 [&_button]:py-2.5 [&_button]:transition-colors [&_button:hover]:bg-violet-400/35 [&_button:hover]:text-white [&_button:focus-visible]:outline-none [&_button:focus-visible]:ring-2 [&_button:focus-visible]:ring-violet-300 [&_button:focus-visible]:ring-offset-2 [&_button:focus-visible]:ring-offset-[#2A4F61] [&_button[data-state=active]]:bg-violet-400/40 [&_button[data-state=active]]:text-white [&_button[data-state=active]]:border-l-4 [&_button[data-state=active]]:border-violet-300 [&_button[data-state=active]]:shadow-sm'
      : themeAdmin
        ? 'flex h-auto w-full flex-col bg-transparent p-1.5 gap-0.5 [&_button]:text-slate-300 [&_button]:rounded-lg [&_button]:px-3 [&_button]:py-2.5 [&_button:hover]:bg-white/10 [&_button:hover]:text-white [&_button[data-state=active]]:bg-violet-500/25 [&_button[data-state=active]]:text-white [&_button[data-state=active]]:border-l-2 [&_button[data-state=active]]:border-violet-400'
        : 'flex h-auto w-full flex-col bg-transparent p-1'

  return (
    <div className={cn('relative min-h-screen', rootBgClass)} data-theme={dataTheme}>
      {/* Same background image as login page — full cover behind glass UI */}
      <div
        className="fixed inset-0 bg-cover bg-center bg-no-repeat -z-10"
        style={{ backgroundImage: `url(${changeIqBg})` }}
        aria-hidden
      />
      <div className="fixed inset-0 bg-slate-900/50 -z-[5]" aria-hidden />
      <div className="relative z-0 mx-auto max-w-7xl px-4 py-5 sm:px-6 lg:px-8">
        {/* Sticky header — dark glass to suit background */}
        <div className="sticky top-0 z-20 -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8 py-4 mb-6 border-b border-white/10 bg-slate-800/75 backdrop-blur-xl shadow-lg">
          <div className="flex items-center justify-between gap-4">
            <div className={cn('min-w-0', headerBorderClass)}>
              <h1 className={cn(titleClass, 'truncate')}>NPCI AI Agent Portal</h1>
              <p className={cn(subtitleClass, 'truncate')}>
                {user === 'Product' && 'Product Owner Dashboard'}
                {user === 'Developer' && 'Developer Dashboard'}
                {user === 'Admin' && 'Admin Dashboard'}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="hidden sm:flex items-center gap-2 rounded-lg border border-white/20 bg-white/10 backdrop-blur-sm px-3 py-2 text-sm">
                <User className="h-4 w-4 text-slate-400" />
                <span className="font-medium text-slate-200">{user}</span>
              </div>
              <Button variant="outline" onClick={handleLogout} className="border-white/30 text-black hover:bg-white/15 hover:text-white shadow-sm">
                <LogOut className="mr-2 h-4 w-4" />
                Logout
              </Button>
            </div>
          </div>
        </div>

        <div data-theme-content>
          {showProductTabs ? (
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <div className="grid gap-6 lg:grid-cols-[260px_1fr] lg:items-stretch">
                {/* Sidebar nav (desktop) — full left column uses role color */}
                <aside className={cn('hidden lg:block lg:min-h-[400px] py-4 pl-4 pr-3', sidebarAsideClass)}>
                  <Card className={sidebarCardClass}>
                    <CardHeader className="pb-3 px-1">
                      <CardTitle className={cn('text-base', sidebarHeaderClass)}>Sections</CardTitle>
                      <CardDescription className={sidebarDescClass}>Navigate product workflows</CardDescription>
                    </CardHeader>
                    <CardContent className="p-0 pt-0">
                      <TabsList className={sidebarTabsClass}>
                        <TabsTrigger value="change-requests" className="w-full justify-start gap-2.5 py-2.5">
                          <FileText className="h-4 w-4 shrink-0" />
                          Change Requests
                        </TabsTrigger>
                        <TabsTrigger value="status" className="w-full justify-start gap-2.5 py-2.5">
                          <Clock className="h-4 w-4 shrink-0" />
                          Change Management
                        </TabsTrigger>
                        <TabsTrigger value="publish" className="w-full justify-start gap-2.5 py-2.5">
                          <Send className="h-4 w-4 shrink-0" />
                          Status Center
                        </TabsTrigger>
                      </TabsList>
                    </CardContent>
                  </Card>
                </aside>

                {/* Main content — elevated glass panel */}
                <div className="min-w-0 rounded-2xl border border-white/25 bg-white/20 backdrop-blur-xl shadow-2xl p-4 sm:p-6 ring-1 ring-white/10" data-portal-glass>
                  {/* Top nav (mobile) */}
                  <div className="lg:hidden mb-4">
                    <TabsList className="grid w-full grid-cols-3 bg-slate-800/60 border border-white/15 p-1 rounded-xl">
                      <TabsTrigger value="change-requests" className="data-[state=active]:bg-white/20 data-[state=active]:text-white rounded-lg">Change Requests</TabsTrigger>
                      <TabsTrigger value="status" className="data-[state=active]:bg-white/20 data-[state=active]:text-white rounded-lg">Change Management</TabsTrigger>
                      <TabsTrigger value="publish" className="data-[state=active]:bg-white/20 data-[state=active]:text-white rounded-lg">Status Center</TabsTrigger>
                    </TabsList>
                  </div>

                  <TabsContent value="change-requests" className="mt-0 data-[state=active]:animate-in data-[state=active]:fade-in-0 data-[state=active]:slide-in-from-bottom-1">
                    <ChangeRequestsTab onSubmitted={() => setActiveTab('status')} />
                  </TabsContent>

                  <TabsContent value="status" className="mt-0 data-[state=active]:animate-in data-[state=active]:fade-in-0 data-[state=active]:slide-in-from-bottom-1">
                    <StatusCenterTab isActive={activeTab === 'status'} showClearAll={false} />
                  </TabsContent>

                  <TabsContent value="publish" className="mt-0 data-[state=active]:animate-in data-[state=active]:fade-in-0 data-[state=active]:slide-in-from-bottom-1">
                    <PublishChangesTab />
                  </TabsContent>
                </div>
              </div>
            </Tabs>
          ) : showDeveloperTabs ? (
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <div className="grid gap-6 lg:grid-cols-[260px_1fr] lg:items-stretch">
                <aside className={cn('hidden lg:block lg:min-h-[400px] py-4 pl-4 pr-3', sidebarAsideClass)}>
                  <Card className={sidebarCardClass}>
                    <CardHeader className="pb-3 px-1">
                      <CardTitle className={cn('text-base', sidebarHeaderClass)}>Sections</CardTitle>
                      <CardDescription className={sidebarDescClass}>Developer review & creation</CardDescription>
                    </CardHeader>
                    <CardContent className="p-0 pt-0">
                      <TabsList className={sidebarTabsClass}>
                        <TabsTrigger value="change-requests" className="w-full justify-start gap-2.5 py-2.5">
                          <FileCode className="h-4 w-4 shrink-0" />
                          Change Requests
                        </TabsTrigger>
                        <TabsTrigger value="create-request" className="w-full justify-start gap-2.5 py-2.5">
                          <Sparkles className="h-4 w-4 shrink-0" />
                          Create Request
                        </TabsTrigger>
                      </TabsList>
                    </CardContent>
                  </Card>
                </aside>

                {/* Main content — elevated glass panel */}
                <div className="min-w-0 rounded-2xl border border-white/25 bg-white/20 backdrop-blur-xl shadow-2xl p-4 sm:p-6 ring-1 ring-white/10" data-portal-glass>
                  <div className="lg:hidden mb-4">
                    <TabsList className="grid w-full grid-cols-2 bg-slate-800/60 border border-white/15 p-1 rounded-xl">
                      <TabsTrigger value="change-requests" className="data-[state=active]:bg-white/20 data-[state=active]:text-white rounded-lg">Change Requests</TabsTrigger>
                      <TabsTrigger value="create-request" className="data-[state=active]:bg-white/20 data-[state=active]:text-white rounded-lg">Create Request</TabsTrigger>
                    </TabsList>
                  </div>

                  <TabsContent value="change-requests" className="mt-0 data-[state=active]:animate-in data-[state=active]:fade-in-0 data-[state=active]:slide-in-from-bottom-1">
                    <DeveloperChangeRequestsTab isActive={activeTab === 'change-requests'} />
                  </TabsContent>
                  <TabsContent value="create-request" className="mt-0 data-[state=active]:animate-in data-[state=active]:fade-in-0 data-[state=active]:slide-in-from-bottom-1">
                    <ChangeRequestsTab />
                  </TabsContent>
                </div>
              </div>
            </Tabs>
          ) : showAdminTabs ? (
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <div className="grid gap-6 lg:grid-cols-[260px_1fr] lg:items-stretch">
                <aside className={cn('hidden lg:block lg:min-h-[400px] py-4 pl-4 pr-3', sidebarAsideClass)}>
                  <Card className={sidebarCardClass}>
                    <CardHeader className="pb-3 px-1">
                      <CardTitle className={cn('text-base', sidebarHeaderClass)}>Sections</CardTitle>
                      <CardDescription className={sidebarDescClass}>Admin controls & oversight</CardDescription>
                    </CardHeader>
                    <CardContent className="p-0 pt-0">
                      <TabsList className={sidebarTabsClass}>
                        <TabsTrigger value="change-requests" className="w-full justify-start gap-2.5 py-2.5">
                          <FileText className="h-4 w-4 shrink-0" />
                          Change Requests
                        </TabsTrigger>
                        <TabsTrigger value="status" className="w-full justify-start gap-2.5 py-2.5">
                          <Clock className="h-4 w-4 shrink-0" />
                          Change Management
                        </TabsTrigger>
                        <TabsTrigger value="publish" className="w-full justify-start gap-2.5 py-2.5">
                          <Send className="h-4 w-4 shrink-0" />
                          Status Center
                        </TabsTrigger>
                        <TabsTrigger value="developer-requests" className="w-full justify-start gap-2.5 py-2.5">
                          <FileCode className="h-4 w-4 shrink-0" />
                          Developer Requests
                        </TabsTrigger>
                        <TabsTrigger value="access-management" className="w-full justify-start gap-2.5 py-2.5">
                          <User className="h-4 w-4 shrink-0" />
                          Access Management
                        </TabsTrigger>
                      </TabsList>
                    </CardContent>
                  </Card>
                </aside>

                {/* Main content — elevated glass panel */}
                <div className="min-w-0 rounded-2xl border border-white/25 bg-white/20 backdrop-blur-xl shadow-2xl p-4 sm:p-6 ring-1 ring-white/10" data-portal-glass>
                  <div className="lg:hidden mb-4">
                    <TabsList className="grid w-full grid-cols-2 sm:grid-cols-5 bg-slate-800/60 border border-white/15 p-1 rounded-xl">
                      <TabsTrigger value="change-requests" className="data-[state=active]:bg-white/20 data-[state=active]:text-white rounded-lg text-xs sm:text-sm">Change Requests</TabsTrigger>
                      <TabsTrigger value="status" className="data-[state=active]:bg-white/20 data-[state=active]:text-white rounded-lg text-xs sm:text-sm">Change Management</TabsTrigger>
                      <TabsTrigger value="publish" className="data-[state=active]:bg-white/20 data-[state=active]:text-white rounded-lg text-xs sm:text-sm">Status Center</TabsTrigger>
                      <TabsTrigger value="developer-requests" className="data-[state=active]:bg-white/20 data-[state=active]:text-white rounded-lg text-xs sm:text-sm">Developer</TabsTrigger>
                      <TabsTrigger value="access-management" className="data-[state=active]:bg-white/20 data-[state=active]:text-white rounded-lg text-xs sm:text-sm">Access</TabsTrigger>
                    </TabsList>
                  </div>

                  <TabsContent value="change-requests" className="mt-0 data-[state=active]:animate-in data-[state=active]:fade-in-0 data-[state=active]:slide-in-from-bottom-1">
                    <ChangeRequestsTab onSubmitted={() => setActiveTab('status')} />
                  </TabsContent>

                  <TabsContent value="status" className="mt-0 data-[state=active]:animate-in data-[state=active]:fade-in-0 data-[state=active]:slide-in-from-bottom-1">
                    <StatusCenterTab isActive={activeTab === 'status'} showClearAll={true} />
                  </TabsContent>

                  <TabsContent value="publish" className="mt-0 data-[state=active]:animate-in data-[state=active]:fade-in-0 data-[state=active]:slide-in-from-bottom-1">
                    <PublishChangesTab />
                  </TabsContent>

                  <TabsContent value="developer-requests" className="mt-0 data-[state=active]:animate-in data-[state=active]:fade-in-0 data-[state=active]:slide-in-from-bottom-1">
                    <DeveloperChangeRequestsTab isActive={activeTab === 'developer-requests'} />
                  </TabsContent>

                  <TabsContent value="access-management" className="mt-0 data-[state=active]:animate-in data-[state=active]:fade-in-0 data-[state=active]:slide-in-from-bottom-1">
                    <AccessManagementTab />
                  </TabsContent>
                </div>
              </div>
            </Tabs>
          ) : (
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle>Access Restricted</CardTitle>
                <CardDescription>
                  Please contact administrator for access.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  This section is currently only available for Product Owners, Developers, and Admins.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

function ChangeRequestsTab({ onSubmitted }) {
  const [apiName, setApiName] = useState('')
  const [changeType, setChangeType] = useState('')
  const [description, setDescription] = useState('')
  const [productNoteSummary, setProductNoteSummary] = useState('')
  const [productNoteFile, setProductNoteFile] = useState(null)
  // Phase 2: unified artifacts (sampleRequests = former dumpLog, existingXsd = former currentXsd)
  const [sampleRequests, setSampleRequests] = useState(null)
  const [sampleResponses, setSampleResponses] = useState(null)
  const [existingXsd, setExistingXsd] = useState(null)
  const [proposedXsd, setProposedXsd] = useState(null)
  const [brdDocuments, setBrdDocuments] = useState(null)
  const [currentXsdContent, setCurrentXsdContent] = useState('')
  const [filteredApis, setFilteredApis] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [loading, setLoading] = useState(false)
  const [generatingXsd, setGeneratingXsd] = useState(false)
  const [generatedXsd, setGeneratedXsd] = useState('')
  const [showXsdView, setShowXsdView] = useState(false)
  const [copied, setCopied] = useState(null) // 'current' | 'generated' | null
  // Field Addition: schema input + multi-field additions (XSD-driven)
  const [fieldSchemaMode, setFieldSchemaMode] = useState('upload-xsd') // upload-xsd | upload-sample
  const [fieldSchemaXsdFile, setFieldSchemaXsdFile] = useState(null)
  const [fieldSchemaSampleFile, setFieldSchemaSampleFile] = useState(null)
  const [fieldSchemaLoading, setFieldSchemaLoading] = useState(false)
  const [xsdElements, setXsdElements] = useState([])
  const [xsdAttributesByElement, setXsdAttributesByElement] = useState({})
  const [fieldAdditions, setFieldAdditions] = useState([
    {
      id: 'field-1',
      element: '',
      attributeMode: 'from-xsd', // from-xsd | custom
      attribute: '',
      customAttribute: '',
      mandatory: 'optional', // optional | mandatory
      datatype: 'xs:string',
      allowedValues: '',
      description: '',
    },
  ])
  // Update Java DTO from XSD
  const [dtoXsdFileOverride, setDtoXsdFileOverride] = useState(null)
  const [generateDtoLoading, setGenerateDtoLoading] = useState(false)
  const [dtoResult, setDtoResult] = useState(null)
  const [dtoResultModalOpen, setDtoResultModalOpen] = useState(false)
  const dtoFileInputRef = useRef(null)
  // Code changes from Apply XSD→Java (after Submit)
  const [codeChangesModalOpen, setCodeChangesModalOpen] = useState(false)
  const [codeChangesData, setCodeChangesData] = useState(null)
  // (Supporting Documents accordion removed; BRD upload kept)
  // Backend E2E: spec step after submit (api-addition only)
  const [specStep, setSpecStep] = useState(null) // null | { changeId, oldXsd, newXsd, approvalStatus }
  // Api Addition: CR id "CHG-3digit" set when dump is uploaded; reused for Generate XSD / Submit
  const [apiAdditionChangeId, setApiAdditionChangeId] = useState(null)
  const [sampleDumpUploadSuccess, setSampleDumpUploadSuccess] = useState(false)
  const [sampleDumpUploading, setSampleDumpUploading] = useState(false)

  // Reset form when change type changes
  const handleChangeTypeChange = (value) => {
    setChangeType(value)
    setApiName('')
    setSampleRequests(null)
    setSampleResponses(null)
    setExistingXsd(null)
    setProposedXsd(null)
    setBrdDocuments(null)
    setCurrentXsdContent('')
    setDescription('')
    setProductNoteSummary('')
    setProductNoteFile(null)
    setGeneratedXsd('')
    setShowXsdView(false)
    setFieldSchemaMode('upload-xsd')
    setFieldSchemaXsdFile(null)
    setFieldSchemaSampleFile(null)
    setFieldSchemaLoading(false)
    setXsdElements([])
    setXsdAttributesByElement({})
    setFieldAdditions([
      {
        id: 'field-1',
        element: '',
        attributeMode: 'from-xsd',
        attribute: '',
        customAttribute: '',
        mandatory: 'optional',
        datatype: 'xs:string',
        allowedValues: '',
        description: '',
      },
    ])
    setDtoXsdFileOverride(null)
    setDtoResult(null)
    setDtoResultModalOpen(false)
    setSpecStep(null)
    setApiAdditionChangeId(null)
    setSampleDumpUploadSuccess(false)
    setSampleDumpUploading(false)
  }

  // Read existing/current XSD file content when uploaded (for comparison view)
  const handleExistingXsdChange = async (e) => {
    const file = e.target.files?.[0]
    if (file) {
      setExistingXsd(file)
      try {
        const text = await readFileTextSmart(file)
        setCurrentXsdContent(text)
      } catch {
        // Fallback to legacy behavior
        const reader = new FileReader()
        reader.onload = (event) => {
          setCurrentXsdContent(event.target.result)
        }
        reader.readAsText(file)
      }
    }
  }

  // Api Addition: on dump file select, call POST /agent/artifact/upload; on success highlight green
  const handleSampleDumpChange = async (e) => {
    const file = e?.target?.files?.[0] ?? null
    setSampleRequests(file)
    if (!file) {
      setSampleDumpUploadSuccess(false)
      setApiAdditionChangeId(null)
      return
    }
    if (changeType === 'api-addition') {
      setSampleDumpUploading(true)
      setSampleDumpUploadSuccess(false)
      try {
        const changeId = apiAdditionChangeId || generateCrId3digit()
        if (!apiAdditionChangeId) setApiAdditionChangeId(changeId)
        await uploadArtifact(changeId, 'sampleRequests', file)
        setSampleDumpUploadSuccess(true)
      } catch (err) {
        setSampleDumpUploadSuccess(false)
        const msg = err?.response?.data?.detail ?? err?.message ?? 'Upload failed'
        alert(`Upload failed: ${msg}`)
      } finally {
        setSampleDumpUploading(false)
      }
    }
  }

  const inferApiNameFromXsd = (elements) => {
    if (!Array.isArray(elements) || elements.length === 0) return ''
    const match = elements.find((e) => API_OPTIONS.includes(e))
    return match || elements[0] || ''
  }

  const setSchemaFromXsdText = (xsdText) => {
    const text = String(xsdText || '').replace(/^\uFEFF/, '').replace(/\u0000/g, '').trim()
    const parsed = parseXsdElementsAndAttributes(text)
    if (!parsed?.elements?.length) {
      // Invalid or unsupported XSD (or parse error). Don't ingest it.
      toast.error('Invalid XSD', 'Please upload a valid .xsd (XML schema).')
      setCurrentXsdContent('')
      setXsdElements([])
      setXsdAttributesByElement({})
      setGeneratedXsd('')
      setShowXsdView(false)
      return
    }

    setCurrentXsdContent(text)
    setXsdElements(parsed.elements || [])
    setXsdAttributesByElement(parsed.attributesByElement || {})

    // Reset generated XSD view when baseline changes
    setGeneratedXsd('')
    // For Field Addition / Field value changes, show baseline immediately
    setShowXsdView(changeType === 'field-addition' || changeType === 'field-value-changes')

    // Auto-populate API Name from XSD (best-effort)
    if (!apiName?.trim()) {
      const inferred = inferApiNameFromXsd(parsed.elements || [])
      if (inferred) setApiName(inferred)
    }

    // Reset field rows that depend on schema choices
    setFieldAdditions((prev) =>
      (prev && prev.length ? prev : []).map((r, idx) => ({
        ...r,
        id: r.id || `field-${idx + 1}`,
        element: '',
        attributeMode: 'from-xsd',
        attribute: '',
        customAttribute: '',
      }))
    )
  }

  const readFileTextSmart = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onerror = () => reject(new Error('Failed to read file'))
      reader.onload = () => {
        try {
          const buf = reader.result
          const bytes = new Uint8Array(buf)
          const b0 = bytes[0]
          const b1 = bytes[1]
          const b2 = bytes[2]

          // Detect BOM
          const isUtf16le = b0 === 0xff && b1 === 0xfe
          const isUtf16be = b0 === 0xfe && b1 === 0xff
          const isUtf8bom = b0 === 0xef && b1 === 0xbb && b2 === 0xbf

          // Decode
          if (isUtf16be) {
            // TextDecoder doesn't reliably support utf-16be in all environments; swap bytes and decode as utf-16le.
            const swapped = new Uint8Array(bytes.length)
            for (let i = 0; i + 1 < bytes.length; i += 2) {
              swapped[i] = bytes[i + 1]
              swapped[i + 1] = bytes[i]
            }
            const td = new TextDecoder('utf-16le')
            return resolve(td.decode(swapped))
          }
          if (isUtf16le) {
            const td = new TextDecoder('utf-16le')
            return resolve(td.decode(bytes))
          }
          // default UTF-8 (with or without BOM)
          const td = new TextDecoder('utf-8')
          return resolve(td.decode(bytes))
        } catch (err) {
          reject(err)
        }
      }
      reader.readAsArrayBuffer(file)
    })
  }

  const formatXml = (xml) => {
    const input = String(xml || '').trim()
    if (!input) return ''
    // Very small pretty-printer: insert newlines between tags and indent.
    const withNewlines = input.replace(/(>)(<)(\/*)/g, '$1\n$2$3')
    const lines = withNewlines.split('\n')
    let indent = 0
    const pad = (n) => '  '.repeat(Math.max(0, n))
    return lines
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        if (line.match(/^<\/.+>/)) indent -= 1
        const out = pad(indent) + line
        if (line.match(/^<[^!?/].*[^/]>$/) && !line.includes('</')) indent += 1
        return out
      })
      .join('\n')
  }

  // Field Addition / Field value changes: auto-generate the updated XSD as user edits fields (no button)
  useEffect(() => {
    const isFieldSchemaChange = changeType === 'field-addition' || changeType === 'field-value-changes'
    if (!isFieldSchemaChange) return
    if (!currentXsdContent?.trim()) {
      setGeneratedXsd('')
      return
    }
    try {
      const next = applyFieldAdditionsToXsd(currentXsdContent, fieldAdditions, { mode: changeType })
      setGeneratedXsd((prev) => (prev === next ? prev : next))
      setShowXsdView(true)
    } catch {
      // Keep current output if parse fails mid-edit
    }
  }, [changeType, currentXsdContent, fieldAdditions])

  const handleFieldXsdUpload = async (e) => {
    const file = e?.target?.files?.[0] ?? null
    setFieldSchemaXsdFile(file)
    setFieldSchemaSampleFile(null)
    if (!file) {
      setCurrentXsdContent('')
      setXsdElements([])
      setXsdAttributesByElement({})
      return
    }
    try {
      const text = await readFileTextSmart(file)
      setSchemaFromXsdText(text)
    } catch {
      const reader = new FileReader()
      reader.onload = (event) => setSchemaFromXsdText(event.target?.result)
      reader.readAsText(file)
    }
  }

  const handleFieldSampleUpload = async (e) => {
    const file = e?.target?.files?.[0] ?? null
    setFieldSchemaSampleFile(file)
    setFieldSchemaXsdFile(null)
    if (!file) {
      setCurrentXsdContent('')
      setXsdElements([])
      setXsdAttributesByElement({})
      return
    }
    setFieldSchemaLoading(true)
    try {
      const res = await changeRequestAPI.convertSampleXmlToXsd(file)
      const xsd = res?.data?.xsd
      if (!xsd) throw new Error('No XSD returned from conversion API')
      setSchemaFromXsdText(xsd)
    } catch (err) {
      const msg = err?.response?.data?.detail ?? err?.message ?? 'Failed to convert sample XML to XSD'
      alert(msg)
    } finally {
      setFieldSchemaLoading(false)
    }
  }

  const applyFieldAdditionsToXsd = (baseXsd, additions, opts = {}) => {
    const mode = opts?.mode || 'field-addition' // field-addition | field-value-changes
    const cleaned = String(baseXsd || '').replace(/^\uFEFF/, '').trim()
    const doc = new DOMParser().parseFromString(cleaned, 'text/xml')
    if (!doc?.documentElement) throw new Error('Invalid XSD')

    const all = doc.getElementsByTagName('*')
    // Stop if we parsed an error document
    for (let i = 0; i < all.length; i++) {
      if (all[i]?.localName === 'parsererror') {
        throw new Error('Invalid XSD (XML parse error)')
      }
    }

    const schemaEl = Array.from(all).find((n) => n.localName === 'schema' && String(n.namespaceURI || '').includes('http://www.w3.org/2001/XMLSchema'))
    if (!schemaEl) {
      throw new Error('Invalid XSD (missing xs:schema)')
    }
    const schemaPrefix = schemaEl?.prefix || 'xs'
    const ns = 'http://www.w3.org/2001/XMLSchema'
    const create = (localName) => doc.createElementNS(ns, `${schemaPrefix}:${localName}`)

    // Index complexTypes by name so element@type can be resolved.
    const complexTypesByName = new Map()
    for (let i = 0; i < all.length; i++) {
      const node = all[i]
      if (node.localName === 'complexType') {
        const n = node.getAttribute('name')
        if (n) complexTypesByName.set(n, node)
      }
    }

    const findElementNodeByName = (name) => {
      for (let i = 0; i < all.length; i++) {
        const node = all[i]
        if (node.localName === 'element' && node.getAttribute('name') === name) return node
      }
      return null
    }

    const ensureComplexTypeNode = (elementNode) => {
      // Inline complexType?
      for (let c = 0; c < elementNode.childNodes.length; c++) {
        const child = elementNode.childNodes[c]
        if (child?.nodeType === 1 && child.localName === 'complexType') return child
      }
      // Referenced complexType by type?
      const typeRef = elementNode.getAttribute('type')
      if (typeRef) {
        const localType = String(typeRef).split(':').pop()
        if (complexTypesByName.has(typeRef)) return complexTypesByName.get(typeRef)
        if (complexTypesByName.has(localType)) return complexTypesByName.get(localType)
      }

      // Otherwise create inline complexType
      const ct = create('complexType')
      elementNode.appendChild(ct)
      return ct
    }

    const findAttributeNode = (complexTypeNode, attrName) => {
      const subtree = complexTypeNode.getElementsByTagName('*')
      for (let i = 0; i < subtree.length; i++) {
        const n = subtree[i]
        if (n.localName === 'attribute' && n.getAttribute('name') === attrName) return n
      }
      return null
    }

    const applyAttributeShape = (attrNode, { datatype, mandatory, allowedValues }) => {
      // use required/optional
      attrNode.setAttribute('use', mandatory === 'mandatory' ? 'required' : 'optional')

      // Remove existing @type if we will add simpleType
      const trimmedAllowed = String(allowedValues || '').trim()
      if (trimmedAllowed) {
        attrNode.removeAttribute('type')
        // remove existing simpleType children
        const children = Array.from(attrNode.childNodes).filter((n) => n?.nodeType === 1)
        for (const c of children) {
          attrNode.removeChild(c)
        }

        const simpleType = create('simpleType')
        const restriction = create('restriction')
        restriction.setAttribute('base', datatype || 'xs:string')
        trimmedAllowed
          .split(/[,\n]/g)
          .map((s) => s.trim())
          .filter(Boolean)
          .forEach((val) => {
            const en = create('enumeration')
            en.setAttribute('value', val)
            restriction.appendChild(en)
          })
        simpleType.appendChild(restriction)
        attrNode.appendChild(simpleType)
      } else {
        // No allowed-values: make it typed
        // remove children (simpleType)
        const children = Array.from(attrNode.childNodes).filter((n) => n?.nodeType === 1)
        for (const c of children) {
          attrNode.removeChild(c)
        }
        attrNode.setAttribute('type', datatype || 'xs:string')
      }
    }

    const addOrUpdateAttribute = (complexTypeNode, { name, datatype, mandatory, allowedValues }) => {
      const existing = findAttributeNode(complexTypeNode, name)
      if (existing) {
        // For Field value changes we update existing attributes; for Field Addition we leave them unchanged.
        if (mode === 'field-value-changes') {
          applyAttributeShape(existing, { datatype, mandatory, allowedValues })
        }
        return
      }

      const attr = create('attribute')
      attr.setAttribute('name', name)
      applyAttributeShape(attr, { datatype, mandatory, allowedValues })

      complexTypeNode.appendChild(attr)
    }

    for (const row of additions || []) {
      const element = (row.element || '').trim()
      const attribute =
        row.attributeMode === 'custom' ? (row.customAttribute || '').trim() : (row.attribute || '').trim()
      if (!element || !attribute) continue
      const elNode = findElementNodeByName(element)
      if (!elNode) continue
      const ct = ensureComplexTypeNode(elNode)
      addOrUpdateAttribute(ct, {
        name: attribute,
        datatype: row.datatype,
        mandatory: row.mandatory,
        allowedValues: row.allowedValues,
      })
    }

    return new XMLSerializer().serializeToString(doc)
  }

  // Generate XSD: Api Addition uses backend (upload samples → spec/generate); others use stub
  const handleGenerateXsd = async () => {
    if (isFieldAddition) {
      if (!currentXsdContent?.trim()) {
        alert('For Field Addition, upload XSD or upload sample XML (to convert to XSD) first.')
        return
      }
      const hasAny = (fieldAdditions || []).some((r) => {
        const element = (r.element || '').trim()
        const attr = r.attributeMode === 'custom' ? (r.customAttribute || '').trim() : (r.attribute || '').trim()
        return Boolean(element && attr)
      })
      if (!hasAny) {
        alert('Add at least one field (Element + Field Attribute) to generate XSD.')
        return
      }
    } else {
      if (!apiName.trim()) {
        alert('API Name is required to generate XSD')
        return
      }
      if (isApiAddition && (!sampleRequests || !sampleDumpUploadSuccess)) {
        alert('Upload sample dump first and wait for it to succeed (green) before generating XSD')
        return
      }
      if (!isApiAddition && !description.trim()) {
        alert('Description is required to generate XSD')
        return
      }
    }

    setGeneratingXsd(true)
    setShowXsdView(true)

    try {
      // Api Addition: call only spec/generate (upload is done when user uploads document — UI turns green)
      if (isApiAddition) {
        const changeId = apiAdditionChangeId || generateCrId3digit()
        if (!apiAdditionChangeId) setApiAdditionChangeId(changeId)

        const res = await specGenerate({
          change_id: changeId,
          apiName: apiName.trim(),
          changeType: 'ADD_NEW_API',
          description: description || '',
        })
        const newXsd = res?.data?.newXsd
        if (newXsd != null) {
          setGeneratedXsd(newXsd)
        } else {
          throw new Error('No XSD in response from spec/generate')
        }
        return
      }

      // Field Addition: apply all requested fields to the baseline XSD (client-side)
      if (isFieldAddition) {
        const updated = applyFieldAdditionsToXsd(currentXsdContent, fieldAdditions)
        setGeneratedXsd(updated)
        return
      }

      // Other change types: use stub (no backend XSD generator for these)
      const changeId = `CHG-${Date.now()}`
      const payload = {
        changeId,
        description: description || '',
        changeType,
        fieldName: apiName,
        apiName: apiName || undefined,
      }
      const response = await changeRequestAPI.generateXsd(payload)
      if (response.data && response.data.xsd) {
        setGeneratedXsd(response.data.xsd)
      } else {
        throw new Error('Invalid response from XSD generation API')
      }
    } catch (error) {
      console.error('Error generating XSD:', error)
      let detail = 'Please try again.'
      if (error.response?.data?.detail) {
        const d = error.response.data.detail
        detail = Array.isArray(d) ? (d[0]?.msg || d.map((e) => e.msg).filter(Boolean).join('; ') || JSON.stringify(d)) : String(d)
      } else if (error.response?.data?.error) {
        detail = String(error.response.data.error)
      } else if (error.message) {
        detail = error.message
      }
      alert(`Failed to generate XSD. ${detail}`)
      setShowXsdView(false)
    } finally {
      setGeneratingXsd(false)
    }
  }

  // Copy XSD to clipboard
  const handleCopyXsd = async (xsdContent, source) => {
    try {
      await navigator.clipboard.writeText(xsdContent)
      setCopied(source)
      setTimeout(() => setCopied(null), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
      alert('Failed to copy to clipboard')
    }
  }

  // Update Java DTO from XSD: parse changes, invoke AI, show diff/code in modal
  const handleGenerateDto = async () => {
    const xsdFile = dtoXsdFileOverride || (generatedXsd ? new File([generatedXsd], 'generated.xsd', { type: 'application/xml' }) : null)
    if (!xsdFile) {
      alert('Generate XSD first or choose an XSD file from disk.')
      return
    }
    setGenerateDtoLoading(true)
    setDtoResult(null)
    try {
      const payload = { xsdFile }
      if (currentXsdContent && currentXsdContent.trim()) {
        payload.baselineXsdFile = new File([currentXsdContent], 'baseline.xsd', { type: 'application/xml' })
      }
      const res = await changeRequestAPI.generateDto(payload)
      setDtoResult(res.data || res)
      setDtoResultModalOpen(true)
    } catch (err) {
      setDtoResult({ success: false, error: err.response?.data?.detail || err.message || 'Failed to generate DTO' })
      setDtoResultModalOpen(true)
    } finally {
      setGenerateDtoLoading(false)
    }
  }

  const handleApiNameChange = (value) => {
    setApiName(value)
    // Field Addition: clear schema when API name changes
    if (changeType === 'field-addition') {
      setCurrentXsdContent('')
      setXsdElements([])
      setXsdAttributesByElement({})
      setFieldSchemaXsdFile(null)
      setFieldSchemaSampleFile(null)
      setGeneratedXsd('')
      setShowXsdView(false)
    }
    if (value) {
      const filtered = API_OPTIONS.filter(api =>
        api.toLowerCase().includes(value.toLowerCase())
      )
      setFilteredApis(filtered)
      setShowSuggestions(filtered.length > 0)
    } else {
      setShowSuggestions(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Validation
    if (!changeType) {
      alert('Please select a change type')
      return
    }
    
    if (!description.trim()) {
      alert('Description is required')
      return
    }

    if (description.trim().length < 10) {
      alert('Description must be at least 10 characters.')
      return
    }

    // For Api Addition, Sample Request Files is mandatory
    if (changeType === 'api-addition' && !sampleRequests) {
      alert('Sample Request Files is mandatory for Api Addition')
      return
    }

    // For Api Addition, api name is required
    if (changeType === 'api-addition' && !apiName.trim()) {
      alert('API Name is required for Api Addition')
      return
    }

    // For Element Addition or Field value changes, api name is required
    if ((changeType === 'element-addition' || changeType === 'field-value-changes') && !apiName.trim()) {
      alert('API Name is required')
      return
    }

    // For Field Addition / Field value changes, uploaded schema is required
    if (changeType === 'field-addition' || changeType === 'field-value-changes') {
      if (!apiName?.trim()) {
        alert('API Name is required (auto-populated from XSD when possible)')
        return
      }
      if (!currentXsdContent?.trim()) {
        alert('Upload existing XSD is required')
        return
      }
      const hasAnyField = (fieldAdditions || []).some((r) => {
        const el = (r.element || '').trim()
        const attr = r.attributeMode === 'custom' ? (r.customAttribute || '').trim() : (r.attribute || '').trim()
        return Boolean(el && attr)
      })
      if (!hasAnyField) {
        alert('Add at least one field (Element + Field Attribute)')
        return
      }
    }

    // Api Addition: on Submit, we will run spec/generate + spec/approve automatically.

    setLoading(true)

    try {
      // Api Addition: on Submit, run spec/generate then spec/approve, then fetch patch
      if (changeType === 'api-addition') {
        if (!apiName?.trim()) {
          alert('API Name is required for Api Addition')
          setLoading(false)
          return
        }
        if (!sampleRequests || !sampleDumpUploadSuccess) {
          alert('Upload sample dump first and wait for it to succeed (green) before submitting.')
          setLoading(false)
          return
        }

        const changeId = apiAdditionChangeId || generateCrId3digit()
        if (!apiAdditionChangeId) setApiAdditionChangeId(changeId)

        // 1) POST /npciswitch/spec/generate
        let newXsd = generatedXsd
        try {
          const genRes = await specGenerate({
            change_id: changeId,
            apiName: apiName.trim(),
            changeType: 'ADD_NEW_API',
            description: description || '',
          })
          newXsd = genRes?.data?.newXsd
          if (!newXsd) throw new Error('No newXsd in response')
          setGeneratedXsd(newXsd)
          setShowXsdView(true)
        } catch (err) {
          const msg = err?.response?.data?.detail ?? err?.message ?? 'Spec generate failed'
          alert(`Spec generate failed: ${msg}`)
          onSubmitted?.()
          setLoading(false)
          return
        }

        setLocalChangeRequest({
          changeId,
          description,
          changeType,
          apiName: apiName || undefined,
          currentStatus: 'Pending',
          receivedDate: new Date().toISOString(),
          updatedOn: new Date().toISOString(),
        })
        setSpecStep({
          changeId,
          oldXsd: '',
          newXsd: newXsd,
          approvalStatus: 'PENDING',
        })

        // 2) POST /npciswitch/spec/approve/{changeId} — use response status e.g. {"status":"Waiting for Developer Approval"}
        let statusFromApi = ''
        try {
          const approveRes = await changeRequestAPI.specApprove(changeId)
          statusFromApi = approveRes?.data?.status ?? (approveRes?.data?.error ? null : 'Approved')
          if (statusFromApi) {
            setLocalChangeRequest({ changeId, currentStatus: statusFromApi })
            setSpecStep((s) => (s?.changeId === changeId ? { ...s, approvalStatus: statusFromApi } : s))
          } else {
            throw new Error(approveRes?.data?.error ?? 'No status in response')
          }
        } catch (err) {
          const msg = err?.response?.data?.detail ?? err?.message ?? 'Approve failed'
          alert(`Approve failed: ${msg}`)
          onSubmitted?.()
          setLoading(false)
          return
        }

        // Upload optional product note (manual override; skips agent generation when manifest is created)
        if (productNoteFile) {
          try {
            await uploadArtifact(changeId, 'productNotes', productNoteFile)
          } catch (err) {
            console.warn('Product note upload failed (continuing):', err)
          }
        }

        // Persist CR to backend so it appears on Developer dashboard
        try {
          await changeRequestAPI.saveChangeRequestToBackend({
            changeId,
            description: description || '',
            productNoteSummary: productNoteSummary || undefined,
            changeType: changeType || 'api-addition',
            apiName: apiName || undefined,
            currentStatus: statusFromApi,
            receivedDate: new Date().toISOString(),
            updatedOn: new Date().toISOString(),
          })
        } catch (err) {
          console.warn('Failed to save change request to backend:', err)
        }

        // 3) GET /npciswitch/dev/patch/{changeId}
        try {
          const res = await changeRequestAPI.getDevPatch(changeId)
          const data = res.data
          const files = (data.results || []).map((r) => ({
            // Prefer backend-provided oldCode/newCode for side-by-side diff
            fileName: r.file || 'file',
            filePath: r.file,
            oldCode: r.oldCode ?? '',
            newCode: (r.newCode ?? r.diff) || '',
            diff: r.diff || '',
          }))
          setCodeChangesData({
            changeId,
            description: description || 'Change request',
            files,
          })
          setCodeChangesModalOpen(true)
        } catch (err) {
          const msg = err?.response?.data?.detail ?? err?.response?.data?.message ?? err?.message ?? 'Get patch failed'
          alert(`Get patch failed: ${msg}`)
        }

        onSubmitted?.()
        setLoading(false)
        return
      }

      // Field Addition: use the same backend flow as Api Addition (spec/generate -> approve -> patch)
      if (changeType === 'field-addition') {
        const changeId = generateCrId3digit()

        // Upload optional BRD (so attachment validation can use it if present)
        if (brdDocuments) {
          try {
            await uploadArtifact(changeId, 'brdDocuments', brdDocuments)
          } catch (err) {
            console.warn('BRD upload failed (continuing):', err)
          }
        }

        // Upload optional product note (manual override; skips agent generation when manifest is created)
        if (productNoteFile) {
          try {
            await uploadArtifact(changeId, 'productNotes', productNoteFile)
          } catch (err) {
            console.warn('Product note upload failed (continuing):', err)
          }
        }

        // Upload baseline XSD as an artifact too (optional but helps traceability)
        try {
          const baselineFile = new File([currentXsdContent], `${apiName || 'schema'}.xsd`, { type: 'application/xml' })
          await uploadArtifact(changeId, 'xsd', baselineFile, apiName?.trim())
        } catch (err) {
          console.warn('Baseline XSD upload failed (continuing):', err)
        }

        const normalizeAllowedValues = (s) =>
          String(s || '')
            .split(/[,\n]/g)
            .map((v) => v.trim())
            .filter(Boolean)

        const additions = (fieldAdditions || [])
          .map((r) => {
            const element = (r.element || '').trim()
            const attribute =
              r.attributeMode === 'custom' ? (r.customAttribute || '').trim() : (r.attribute || '').trim()
            if (!element || !attribute) return null
            return {
              xmlPath: `${apiName.trim()}.${element}`,
              elementName: element,
              attributeName: attribute,
              datatype: r.datatype || 'xs:string',
              mandatory: r.mandatory === 'mandatory',
              allowedValues: normalizeAllowedValues(r.allowedValues),
            }
          })
          .filter(Boolean)

        const first = additions[0]

        // 1) POST /npciswitch/spec/generate (existing-api transform)
        try {
          const spec = await specGenerate({
            change_id: changeId,
            apiName: apiName.trim(),
            changeType: 'ADD_XML_ATTRIBUTE',
            description: description || '',
            xsdContent: currentXsdContent,
            fieldAdditions: additions,
            xmlPath: first?.xmlPath,
            elementName: first?.elementName,
            attributeName: first?.attributeName,
            datatype: first?.datatype,
            mandatory: first?.mandatory,
            allowedValues: first?.allowedValues,
          })
          const newXsd = spec?.data?.newXsd
          if (newXsd) {
            setGeneratedXsd(newXsd)
            setShowXsdView(true)
          }
          setSpecStep({
            changeId,
            oldXsd: spec?.data?.oldXsd || '',
            newXsd: newXsd || '',
            approvalStatus: 'PENDING',
          })
          // Persist CR to backend immediately so it appears in Developer dashboard and Find by change ID
          try {
            await changeRequestAPI.saveChangeRequestToBackend({
              changeId,
              description: description || '',
              productNoteSummary: productNoteSummary || undefined,
              changeType: 'field-addition',
              apiName: apiName || undefined,
              currentStatus: 'Waiting for Developer Approval',
              receivedDate: new Date().toISOString(),
              updatedOn: new Date().toISOString(),
            })
          } catch (saveErr) {
            console.warn('Failed to save change request to backend:', saveErr)
          }
          // Automatically approve the spec so getDevPatch returns code changes without a separate Approve click
          try {
            const approveRes = await changeRequestAPI.specApprove(changeId)
            const statusFromApi = approveRes?.data?.status ?? 'Approved'
            setSpecStep((s) => (s?.changeId === changeId ? { ...s, approvalStatus: statusFromApi } : s))
          } catch (approveErr) {
            console.warn('Auto spec approve failed (Get Dev Patch may need manual Approve):', approveErr)
          }

          // 3) GET /npciswitch/dev/patch/{changeId} - to pre-generate and cache the patch
          try {
            await changeRequestAPI.getDevPatch(changeId)
          } catch (err) {
            console.warn('Pre-generating dev patch failed:', err)
          }
        } catch (err) {
          const msg = err?.response?.data?.detail ?? err?.message ?? 'Spec generate failed'
          alert(`Spec generate failed: ${msg}`)
          onSubmitted?.()
          setLoading(false)
          return
        }
        onSubmitted?.()
        setLoading(false)
        return
      }

      // Legacy / other change types: local + stubs
      const createRes = await changeRequestAPI.createChangeRequest({
        description,
        changeType,
        apiName: apiName || undefined,
        generatedXsd: generatedXsd || undefined,
      })
      const changeId = createRes.data.changeId

      const artifacts = [
        { file: sampleRequests, type: 'sampleRequests' },
        { file: sampleResponses, type: 'specs' },
        { file: brdDocuments, type: 'specs' },
        { file: productNoteFile, type: 'productNotes' },
      ]
      for (const { file, type } of artifacts) {
        if (file) {
          try {
            await changeRequestAPI.uploadArtifact(changeId, type, file)
          } catch (err) {
            console.warn('Upload skipped for', type, err)
          }
        }
      }

      const analyzePayload = {
        changeId,
        description,
        changeType,
        fieldName: apiName,
      }
      await changeRequestAPI.analyzeChange(analyzePayload)

      let applyRes = { data: { success: false, files: [] } }
      if (generatedXsd && generatedXsd.trim()) {
        try {
          const applyPayload = {
            changeId,
            xsdContent: generatedXsd,
            baselineXsdContent: currentXsdContent?.trim() || undefined,
          }
          applyRes = await changeRequestAPI.applyXsdToJava(applyPayload)
        } catch (err) {
          console.warn('applyXsdToJava failed:', err)
        }
        if (applyRes.data?.files?.length) {
          try {
            await changeRequestAPI.updateChangeRequestStatus(changeId, { files: applyRes.data.files })
          } catch (err) {
            console.warn('Failed to persist code changes to CR:', err)
          }
        }
      }

      const crWithFiles = { ...createRes.data, files: applyRes.data?.files || [] }
      setCodeChangesData(crWithFiles)
      setCodeChangesModalOpen(true)

      alert(`Change request submitted successfully! Change Request ID: ${changeId}`)
      onSubmitted?.()

      setApiName('')
      setChangeType('')
      setDescription('')
      setSampleRequests(null)
      setSampleResponses(null)
      setExistingXsd(null)
      setProposedXsd(null)
      setBrdDocuments(null)
      setCurrentXsdContent('')
      setGeneratedXsd('')
      setShowXsdView(false)
      setXsdElements([])
      setXsdAttributesByElement({})
      setFieldSchemaMode('upload-xsd')
      setFieldSchemaXsdFile(null)
      setFieldSchemaSampleFile(null)
      setFieldSchemaLoading(false)
      setFieldAdditions([
        {
          id: 'field-1',
          element: '',
          attributeMode: 'from-xsd',
          attribute: '',
          customAttribute: '',
          mandatory: 'optional',
          datatype: 'xs:string',
          allowedValues: '',
          description: '',
        },
      ])
      setSpecStep(null)
    } catch (error) {
      console.error('Error submitting change request:', error)
      let detail = 'Please try again.'
      if (error.response?.data?.detail) {
        const d = error.response.data.detail
        detail = Array.isArray(d) ? (d[0]?.msg || d.map((e) => e.msg).filter(Boolean).join('; ') || JSON.stringify(d)) : String(d)
      } else if (error.response?.data?.error) {
        detail = String(error.response.data.error)
      } else if (error.message) {
        detail = error.message
      }
      alert(`Error submitting change request. ${detail}`)
    } finally {
      setLoading(false)
    }
  }

  const isApiAddition = changeType === 'api-addition'
  const isElementAddition = changeType === 'element-addition'
  const isFieldChange = changeType === 'field-addition' || changeType === 'field-value-changes'
  const isFieldAddition = changeType === 'field-addition'
  const addFieldRow = () => {
    setFieldAdditions((prev) => {
      const nextIdx = (prev?.length || 0) + 1
      return [
        ...(prev || []),
        {
          id: `field-${Date.now()}-${nextIdx}`,
          element: '',
          attributeMode: 'from-xsd',
          attribute: '',
          customAttribute: '',
          mandatory: 'optional',
          datatype: 'xs:string',
          allowedValues: '',
          description: '',
        },
      ]
    })
  }

  const updateFieldRow = (id, patch) => {
    setFieldAdditions((prev) => (prev || []).map((r) => (r.id === id ? { ...r, ...patch } : r)))
  }

  const removeFieldRow = (id) => {
    setFieldAdditions((prev) => {
      const next = (prev || []).filter((r) => r.id !== id)
      return next.length ? next : prev
    })
  }

  // Backend E2E: Approve spec then get dev patch
  const [patchLoading, setPatchLoading] = useState(false)
  const handleSpecApprove = async () => {
    if (!specStep?.changeId) return
    setLoading(true)
    try {
      const res = await changeRequestAPI.specApprove(specStep.changeId)
      const statusFromApi = res?.data?.status ?? (res?.data?.error ? null : 'Approved')
      if (statusFromApi) {
        setLocalChangeRequest({ changeId: specStep.changeId, currentStatus: statusFromApi })
        setSpecStep((s) => (s ? { ...s, approvalStatus: statusFromApi } : s))
        // Persist approved status to backend so Find by change ID and Developer list show it
        try {
          await changeRequestAPI.saveChangeRequestToBackend({
            changeId: specStep.changeId,
            currentStatus: statusFromApi,
            updatedOn: new Date().toISOString(),
          })
        } catch (saveErr) {
          console.warn('Failed to persist approval to backend:', saveErr)
        }
        alert(`Spec approved. Status: ${statusFromApi}`)
      } else {
        throw new Error(res?.data?.error ?? 'No status in response')
      }
    } catch (err) {
      const msg = err?.response?.data?.detail ?? err?.message ?? 'Approve failed'
      alert(`Approve failed: ${msg}`)
    } finally {
      setLoading(false)
    }
  }
  const handleGetPatch = async () => {
    if (!specStep?.changeId) return
    setPatchLoading(true)
    try {
      const res = await changeRequestAPI.getDevPatch(specStep.changeId)
      const data = res.data
      const files = (data.results || []).map((r) => ({
        // Backend now returns oldCode/newCode; fall back to diff string if needed
        fileName: r.file || 'file',
        filePath: r.file,
        oldCode: r.oldCode ?? '',
        newCode: (r.newCode ?? r.diff) || '',
        diff: r.diff || '',
      }))
      setCodeChangesData({
        changeId: specStep.changeId,
        description: description || 'Change request',
        files,
      })
      setCodeChangesModalOpen(true)
    } catch (err) {
      const msg = err?.response?.data?.detail ?? err?.response?.data?.message ?? err?.message ?? 'Get patch failed'
      alert(`Get patch failed: ${msg}`)
    } finally {
      setPatchLoading(false)
    }
  }

  return (
    <>
    <Card>
      <CardHeader className="pb-4">
        <CardTitle className="text-xl">Create Change Request</CardTitle>
        <CardDescription>Submit a new change request for analysis</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Change Type */}
          <div className="space-y-2">
            <Label htmlFor="change-type" className="text-sm font-medium">
              Change Type <span className="text-red-500">*</span>
            </Label>
            <Select value={changeType} onValueChange={handleChangeTypeChange} required>
              <SelectTrigger id="change-type">
                <SelectValue placeholder="Select change type" />
              </SelectTrigger>
              <SelectContent>
                {CHANGE_TYPES.map((type) => (
                  <SelectItem key={type} value={type.toLowerCase().replace(/\s+/g, '-')}>
                    {type}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* API Name */}
          {changeType && (
            <div className="space-y-2">
              <Label htmlFor="api-name" className="text-sm font-medium">
                API Name <span className="text-red-500">*</span>
              </Label>
              {isApiAddition ? (
                <Input
                  id="api-name"
                  placeholder="e.g., ReqPay, ReqRegMob"
                  value={apiName}
                  onChange={(e) => setApiName(e.target.value)}
                  required
                />
              ) : (isFieldChange || isElementAddition) ? (
                <div className="space-y-2">
                  <div className="relative flex gap-2">
                    <div className="relative flex-1">
                      <Input
                        id="api-name"
                        placeholder="e.g. ReqPay, RespPay"
                        value={apiName}
                        onChange={(e) => handleApiNameChange(e.target.value)}
                        onFocus={() => apiName && setShowSuggestions(true)}
                        onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                        required
                      />
                      {showSuggestions && filteredApis.length > 0 && (
                        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-auto">
                          {filteredApis.map((api) => (
                            <div
                              key={api}
                              className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                              onClick={() => {
                                setApiName(api)
                                setShowSuggestions(false)
                              }}
                            >
                              {api}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ) : null}
            </div>
          )}

          {/* Field Addition / Field value changes: Schema input + fields editor */}
          {(changeType === 'field-addition' || changeType === 'field-value-changes') && (
            <div className="space-y-5">
              <div className="border rounded-lg bg-white p-4">
                <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                  <div className="shrink-0">
                    <Label className="text-sm font-medium">Schema input</Label>
                  </div>

                  {changeType === 'field-addition' && (
                    <div className="flex flex-wrap items-center gap-4">
                      <label className="flex items-center gap-2 text-sm text-gray-900 cursor-pointer" title="Behind the scenes: File is read in browser and parsed; elements and attributes are extracted for field dropdowns.">
                        <input
                          type="radio"
                          name="field-schema-mode"
                          value="upload-xsd"
                          checked={fieldSchemaMode === 'upload-xsd'}
                          onChange={() => {
                            setFieldSchemaMode('upload-xsd')
                            setFieldSchemaXsdFile(null)
                            setFieldSchemaSampleFile(null)
                            setCurrentXsdContent('')
                            setXsdElements([])
                            setXsdAttributesByElement({})
                            setGeneratedXsd('')
                            setShowXsdView(false)
                          }}
                        />
                        Upload XSD
                      </label>
                      <label className="flex items-center gap-2 text-sm text-gray-900 cursor-pointer" title="Behind the scenes: Calls POST /agent/xsd/convert-sample-xml; backend converts XML to XSD.">
                        <input
                          type="radio"
                          name="field-schema-mode"
                          value="upload-sample"
                          checked={fieldSchemaMode === 'upload-sample'}
                          onChange={() => {
                            setFieldSchemaMode('upload-sample')
                            setFieldSchemaXsdFile(null)
                            setFieldSchemaSampleFile(null)
                            setCurrentXsdContent('')
                            setXsdElements([])
                            setXsdAttributesByElement({})
                            setGeneratedXsd('')
                            setShowXsdView(false)
                          }}
                        />
                        Upload sample XML
                      </label>
                    </div>
                  )}

                  <div className="flex-1 min-w-[260px]">
                    {(changeType === 'field-value-changes' || fieldSchemaMode === 'upload-xsd') ? (
                      <div className="space-y-1" title="Behind the scenes: File read in browser; elements/attributes parsed for field dropdowns.">
                        <FileUpload
                          accept=".xsd,.xml"
                          onChange={handleFieldXsdUpload}
                          value={fieldSchemaXsdFile}
                        />
                      </div>
                    ) : (
                      <div className="space-y-1" title="Behind the scenes: POST /agent/xsd/convert-sample-xml converts XML to XSD.">
                        <FileUpload
                          accept=".xml,.txt"
                          onChange={handleFieldSampleUpload}
                          value={fieldSchemaSampleFile}
                        />
                        {fieldSchemaLoading && (
                          <p className="text-xs text-[#2F888A]">Converting sample XML to XSD…</p>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold text-gray-900">Fields addition</p>
                    <p className="text-xs text-gray-500 mt-1">
                      Field API name is auto populated from Element + Field Attribute.
                    </p>
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={addFieldRow}
                    disabled={!currentXsdContent?.trim()}
                    className="shrink-0"
                    title="Behind the scenes: Adds a row to fieldAdditions; XSD recomputes in browser with the new attribute."
                  >
                    Add field
                  </Button>
                </div>

                <div className="space-y-3">
                  {fieldAdditions.map((row, idx) => {
                    const attrsForEl = row.element ? (xsdAttributesByElement?.[row.element] || []) : []
                    const effectiveAttr = row.attributeMode === 'custom' ? row.customAttribute : row.attribute
                    const fieldApiName = row.element && effectiveAttr ? `${row.element}.${effectiveAttr}` : ''
                    return (
                      <div key={row.id} className="border rounded-lg bg-white p-4 space-y-4">
                        <div className="flex items-center justify-between gap-3">
                          <p className="text-sm font-medium text-gray-900">Field {idx + 1}</p>
                          {fieldAdditions.length > 1 && (
                            <Button type="button" variant="ghost" onClick={() => removeFieldRow(row.id)} title="Behind the scenes: Removes this field from the list; XSD updates automatically.">
                              Remove
                            </Button>
                          )}
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="space-y-2">
                            <Label className="text-sm font-medium">
                              Element <span className="text-red-500">*</span>
                            </Label>
                            <Select
                              value={row.element}
                              onValueChange={(v) => {
                                const attrsForSelected = xsdAttributesByElement?.[v] || []
                                const firstAttr = Array.isArray(attrsForSelected) ? (attrsForSelected[0] || '') : ''
                                updateFieldRow(row.id, {
                                  element: v,
                                  attributeMode: 'from-xsd',
                                  // Auto-pick first attribute so Field API name auto-populates
                                  attribute: firstAttr,
                                  customAttribute: '',
                                })
                              }}
                              disabled={!currentXsdContent?.trim()}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="Select element" />
                              </SelectTrigger>
                              <SelectContent>
                                {xsdElements.map((name) => (
                                  <SelectItem key={name} value={name}>{name}</SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>

                          <div className="space-y-2">
                            <Label className="text-sm font-medium">
                              Field Attribute <span className="text-red-500">*</span>
                            </Label>
                            <Select
                              value={row.attributeMode === 'custom' ? '__custom__' : (row.attribute || '')}
                              onValueChange={(v) => {
                                if (v === '__custom__') {
                                  updateFieldRow(row.id, { attributeMode: 'custom', attribute: '' })
                                } else {
                                  updateFieldRow(row.id, { attributeMode: 'from-xsd', attribute: v, customAttribute: '' })
                                }
                              }}
                              disabled={!row.element}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder={row.element ? 'Select attribute' : 'Select element first'} />
                              </SelectTrigger>
                              <SelectContent>
                                {attrsForEl.map((a) => (
                                  <SelectItem key={a} value={a}>{a}</SelectItem>
                                ))}
                                <SelectItem value="__custom__">Custom (new)</SelectItem>
                              </SelectContent>
                            </Select>
                            {row.attributeMode === 'custom' && (
                              <Input
                                placeholder="Enter new attribute name"
                                value={row.customAttribute}
                                onChange={(e) => updateFieldRow(row.id, { customAttribute: e.target.value })}
                              />
                            )}
                          </div>

                          <div className="space-y-2">
                            <Label className="text-sm font-medium">Field API name</Label>
                            <Input value={fieldApiName} readOnly placeholder="Auto populated" />
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="space-y-2">
                            <Label className="text-sm font-medium">Mandatory / Optional</Label>
                            <Select value={row.mandatory} onValueChange={(v) => updateFieldRow(row.id, { mandatory: v })}>
                              <SelectTrigger>
                                <SelectValue placeholder="Select" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="mandatory">Mandatory</SelectItem>
                                <SelectItem value="optional">Optional</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>

                          <div className="space-y-2">
                            <Label className="text-sm font-medium">Datatype</Label>
                            <Select value={row.datatype} onValueChange={(v) => updateFieldRow(row.id, { datatype: v })}>
                              <SelectTrigger>
                                <SelectValue placeholder="Select datatype" />
                              </SelectTrigger>
                              <SelectContent>
                                {XSD_TYPE_OPTIONS.map((t) => (
                                  <SelectItem key={t} value={t}>{t}</SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>

                          <div className="space-y-2">
                            <Label className="text-sm font-medium">Allowed field values</Label>
                            <Input
                              placeholder="Comma or newline separated (optional)"
                              value={row.allowedValues}
                              onChange={(e) => updateFieldRow(row.id, { allowedValues: e.target.value })}
                            />
                          </div>
                        </div>

                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description" className="text-sm font-medium">
              Description <span className="text-red-500">*</span>
              <span className="text-gray-500 font-normal ml-1">(at least 10 characters)</span>
            </Label>
            <Textarea
              id="description"
              placeholder="Describe the change request..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              required
              minLength={10}
            />
          </div>

          {/* Product note summary (optional) - included in manifest productNote.summary */}
          <div className="space-y-2">
            <Label htmlFor="productNoteSummary" className="text-sm font-medium text-gray-600">
              Product note summary (optional)
            </Label>
            <Textarea
              id="productNoteSummary"
              placeholder="Brief summary for the manifest product note..."
              value={productNoteSummary}
              onChange={(e) => setProductNoteSummary(e.target.value)}
              rows={2}
            />
          </div>

          {/* Uploads */}
          {changeType && (
            <div className="space-y-4">
              {isApiAddition && (
                <div className="space-y-2">
                  <Label className="text-sm font-medium">
                    Sample Request Files <span className="text-red-500">*</span>
                  </Label>
                  <FileUpload
                    accept=".log,.txt,.json,.xml"
                    onChange={handleSampleDumpChange}
                    value={sampleRequests}
                    required
                    uploadSuccess={sampleDumpUploadSuccess}
                    uploading={sampleDumpUploading}
                  />
                  {sampleDumpUploadSuccess && (
                    <p className="text-xs text-green-600">Dump uploaded to backend</p>
                  )}
                </div>
              )}

              <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                <Label className="text-xs font-medium text-gray-600 sm:w-[160px]">BRD upload (optional)</Label>
                <div className="w-full sm:max-w-md">
                  <FileUpload
                    accept=".pdf,.doc,.docx"
                    onChange={(e) => setBrdDocuments(e.target.files?.[0] || null)}
                    value={brdDocuments}
                  />
                </div>
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                <Label className="text-xs font-medium text-gray-600 sm:w-[160px]">Product note upload (optional)</Label>
                <div className="w-full sm:max-w-md">
                  <FileUpload
                    accept=".pdf,.md,.docx"
                    onChange={(e) => setProductNoteFile(e.target.files?.[0] || null)}
                    value={productNoteFile}
                  />
                  <p className="text-xs text-gray-500 mt-1">PDF, Markdown, or DOCX. If omitted, manifest creation will auto-generate one.</p>
                </div>
              </div>
            </div>
          )}

          {/* After submit: for Field Addition show only "sent to Developer" + change ID; for others show summary + spec step card below */}
          {specStep ? (
            <div className="space-y-4 border-t pt-6 mt-6">
              <div className="p-4 rounded-lg bg-primary/5 border border-primary/20">
                {changeType === 'field-addition' ? (
                  <>
                    <p className="text-sm font-medium text-gray-800">
                      Request being sent to Developer.
                    </p>
                    <p className="text-sm text-gray-700 mt-2">
                      Change ID: <span className="font-mono font-semibold text-primary">{specStep.changeId}</span>
                    </p>
                    <p className="text-xs text-gray-600 mt-1">No further action needed from you. Track in Change Management or create another request.</p>
                  </>
                ) : (
                  <>
                    <p className="text-sm font-medium text-gray-800">
                      Change request submitted. Change ID: <span className="font-mono font-semibold text-primary">{specStep.changeId}</span>
                    </p>
                    <p className="text-xs text-gray-600 mt-1">Track it in Change Management or create another request.</p>
                  </>
                )}
                <div className="flex flex-wrap gap-2 mt-3">
                  <Button type="button" variant="default" size="sm" onClick={() => onSubmitted?.()} title="Behind the scenes: Navigates to Change Management tab to track the CR.">
                    View in Change Management
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setSpecStep(null)}
                    title="Behind the scenes: Resets the form so you can submit a new CR."
                  >
                    Create another request
                  </Button>
                </div>
              </div>
            </div>
          ) : changeType ? (
            <div className="space-y-4 border-t pt-6 mt-6">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-primary" />
                    XSD Generation
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">
                    {isFieldAddition ? 'XSD auto-updates from your selections' : 'Generate XSD schema based on your change request'}
                  </p>
                  {(() => {
                    if (isFieldAddition) {
                      const missing = []
                      if (!apiName?.trim()) missing.push('API Name')
                      if (!currentXsdContent?.trim()) missing.push('Upload XSD / Upload sample')
                      const hasAnyField = (fieldAdditions || []).some((r) => {
                        const el = (r.element || '').trim()
                        const attr = r.attributeMode === 'custom' ? (r.customAttribute || '').trim() : (r.attribute || '').trim()
                        return Boolean(el && attr)
                      })
                      if (!hasAnyField) missing.push('Fields addition (Element + Field Attribute)')
                      if (missing.length > 0) {
                        return (
                          <p className="text-xs text-amber-600 mt-1 flex items-center gap-1">
                            <span>⚠️</span>
                            {missing.join(', ')} to enable generation
                          </p>
                        )
                      }
                    } else {
                      const missingFields = []
                      if (!apiName.trim()) missingFields.push('API Name')
                      if (!description.trim()) missingFields.push('Description')
                      if (isApiAddition && (!sampleRequests || !sampleDumpUploadSuccess)) missingFields.push('Upload sample dump (wait for green)')
                      if (missingFields.length > 0) {
                        return (
                          <p className="text-xs text-amber-600 mt-1 flex items-center gap-1">
                            <span>⚠️</span>
                            Fill in {missingFields.join(', ')} to enable generation
                          </p>
                        )
                      }
                    }
                    return null
                  })()}
                </div>
                {!isFieldAddition && (
                  <Button
                    type="button"
                    onClick={handleGenerateXsd}
                    disabled={generatingXsd || (isApiAddition
                      ? !apiName.trim() || !sampleRequests || !sampleDumpUploadSuccess
                      : !apiName.trim() || !description.trim())}
                    className="shrink-0"
                    variant={((isApiAddition ? (!apiName.trim() || !sampleRequests || !sampleDumpUploadSuccess) : (!apiName.trim() || !description.trim())) ? "outline" : "default")}
                  >
                    {generatingXsd ? (
                      <>
                        <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Generate XSD
                      </>
                    )}
                  </Button>
                )}
              </div>

              {/* XSD View */}
              {showXsdView && (
                <>
                  {isApiAddition && apiAdditionChangeId && (
                    <p className="text-sm text-slate-600 mt-2">
                      Change Request ID: <span className="font-mono font-semibold">{apiAdditionChangeId}</span> (sample dump uploaded via /agent/artifact/upload)
                    </p>
                  )}
                  <div className="mt-4">
                    <Card className="border-2 border-primary/20">
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <FileCode className="h-5 w-5 text-primary" />
                            <CardTitle className="text-base">XSD Schema</CardTitle>
                          </div>
                          {(generatedXsd || currentXsdContent) && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleCopyXsd(formatXml(generatedXsd || currentXsdContent), 'generated')}
                              title="Copy to clipboard"
                            >
                              {copied === 'generated' ? (
                                <Check className="h-4 w-4 text-green-500" />
                              ) : (
                                <Copy className="h-4 w-4" />
                              )}
                            </Button>
                          )}
                        </div>
                      </CardHeader>
                      <CardContent>
                        {generatingXsd ? (
                          <div className="flex flex-col items-center justify-center py-10">
                            <RefreshCw className="h-8 w-8 animate-spin text-primary mb-2" />
                            <p className="text-sm text-gray-600">Generating XSD schema...</p>
                          </div>
                        ) : (generatedXsd || currentXsdContent) ? (
                          <pre className="bg-primary/5 p-4 rounded-md overflow-auto max-h-96 text-xs font-mono border border-primary/20 whitespace-pre">
                            <code className="text-gray-800">{formatXml(generatedXsd || currentXsdContent)}</code>
                          </pre>
                        ) : (
                          <div className="flex flex-col items-center justify-center py-10 text-gray-400">
                            <FileCode className="h-12 w-12 mb-2 opacity-50" />
                            <p className="text-sm">Upload schema to view XSD</p>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                </>
              )}
            </div>
          ) : null}

          {!specStep && (
            <>
              <Button
                type="submit"
                disabled={
                  loading ||
                  !changeType ||
                  generatingXsd ||
                  (isApiAddition
                    ? !apiName.trim() || !sampleRequests || !sampleDumpUploadSuccess
                    : !generatedXsd)
                }
                className="w-full mt-6"
                title={isFieldAddition ? 'Behind the scenes: Uploads BRD & XSD → spec/generate → change-requests → spec/approve → pre-generates Java patch. CR sent to Developer.' : undefined}
              >
                {loading ? (
                  <>Processing...</>
                ) : (
                  <>
                    <Send className="mr-2 h-4 w-4" />
                    {isApiAddition ? 'Submit for approval' : 'Submit Change Request'}
                  </>
                )}
              </Button>
              {changeType && !generatedXsd && !isApiAddition && (
                <p className="text-xs text-center text-gray-500 mt-2">
                  Generate XSD schema to enable submission
                </p>
              )}
              {isApiAddition && !generatedXsd && (
                <p className="text-xs text-center text-gray-500 mt-2">
                  Enter API name, upload sample dump, then click Generate XSD. After XSD is generated, submit for approval.
                </p>
              )}
            </>
          )}
        </form>
      </CardContent>
    </Card>

    {/* Backend E2E: spec step – not shown for Field Addition (no approval/clicks needed from Product); compact when already approved for other types */}
    {specStep && changeType !== 'field-addition' && (
      <Card className="mt-6 border-2 border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            {specStep.approvalStatus && specStep.approvalStatus !== 'PENDING'
              ? 'Change submitted'
              : 'XSD generated for submission'}
          </CardTitle>
          <CardDescription>
            {specStep.approvalStatus && specStep.approvalStatus !== 'PENDING'
              ? `Change ID ${specStep.changeId} — spec approved. Use "Get Dev Patch" to view code changes, or see Change Management.`
              : 'Review old/new XSD below. Approve the spec, then get the dev patch to see code changes.'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-2 p-3 rounded-lg bg-primary/10 border border-primary/20">
            <span className="text-sm font-medium text-gray-700">Change ID:</span>
            <span className="font-mono font-semibold text-primary text-lg">{specStep.changeId}</span>
          </div>
          {/* Only show full current/new XSD when spec is still pending approval */}
          {(!specStep.approvalStatus || specStep.approvalStatus === 'PENDING') && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">Current XSD</p>
                <pre className="bg-gray-50 p-4 rounded border text-xs overflow-auto max-h-64">
                  {specStep.oldXsd || '(none)'}
                </pre>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700 mb-1">Generated XSD (for approval)</p>
                <pre className="bg-primary/5 p-4 rounded border text-xs overflow-auto max-h-64">
                  {specStep.newXsd || '(none)'}
                </pre>
              </div>
            </div>
          )}
          <div className="flex flex-wrap gap-3">
            <Button
              type="button"
              onClick={handleSpecApprove}
              disabled={loading || (specStep.approvalStatus && specStep.approvalStatus !== 'PENDING')}
            >
              {specStep.approvalStatus && specStep.approvalStatus !== 'PENDING' ? specStep.approvalStatus : 'Approve Spec'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={handleGetPatch}
              disabled={patchLoading || !specStep.approvalStatus || specStep.approvalStatus === 'PENDING'}
            >
              {patchLoading ? 'Loading...' : 'Get Dev Patch'}
            </Button>
          </div>
        </CardContent>
      </Card>
    )}

    <CodeComparisonModal
      open={codeChangesModalOpen}
      onOpenChange={setCodeChangesModalOpen}
      changeRequest={codeChangesData}
      showApproveReject={false}
    />
  </>
  )
}

function PublishChangesTab() {
  const [publishSubTab, setPublishSubTab] = useState('publish-manifest')
  return (
    <Card className="text-gray-900">
      <CardHeader>
        <CardTitle className="text-gray-900">Status Center</CardTitle>
        <CardDescription className="text-gray-600">Publish changes to bank endpoints and track delivery status</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={publishSubTab} onValueChange={setPublishSubTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3 max-w-2xl">
            <TabsTrigger value="publish-manifest">By Partner</TabsTrigger>
            <TabsTrigger value="by-change-request">By Change Request</TabsTrigger>
            <TabsTrigger value="orchestrator-report">Orchestrator Report</TabsTrigger>
          </TabsList>
          <TabsContent value="publish-manifest" className="mt-6">
            <PublishManifestSection />
          </TabsContent>
          <TabsContent value="by-change-request" className="mt-6">
            <ByChangeRequestSection />
          </TabsContent>
          <TabsContent value="orchestrator-report" className="mt-6">
            <OrchestratorReportSection />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

const PARTY_STATUS_VARIANTS = {
  RECEIVED: 'secondary',
  APPLIED: 'default',
  TESTED: 'outline',
  TESTS_READY: 'default',
  READY: 'default',
}

// Pill-style stage colors for By Partner tab (reference-style UI)
const PARTY_STAGE_PILL_CLASS = {
  RECEIVED: 'bg-slate-100 text-slate-800 border-0',
  APPLIED: 'bg-[#2F888A]/15 text-[#2F888A] border-0',
  TESTED: 'bg-amber-100 text-amber-800 border-0',
  TESTS_READY: 'bg-orange-100 text-orange-800 border-0',
  READY: 'bg-emerald-100 text-emerald-800 border-0',
}

// Dummy data for "By Change Request" tab to show structure: each change request → banks → status
const DUMMY_ORCHESTRATOR_STATE = {
  'CHG-001': { 'Bank_A': 'RECEIVED', 'Bank_B': 'APPLIED', 'Bank_C': 'TESTED', 'Payer': 'READY' },
  'CHG-002': { 'Bank_A': 'APPLIED', 'Bank_B': 'READY', 'Bank_C': 'RECEIVED', 'Payee': 'TESTED' },
  'CHG-003': { 'Bank_A': 'READY', 'Bank_B': 'READY', 'Bank_C': 'APPLIED', 'Payer': 'TESTED', 'Payee': 'RECEIVED' },
  'CHG-004': { 'Bank_A': 'TESTED', 'Bank_C': 'RECEIVED' }, // Bank_B has no status for this CR
}

const DUMMY_CHANGE_DESCRIPTIONS = {
  'CHG-001': 'Add new optional field to ReqPay schema',
  'CHG-002': 'Extend ReqRegMob with additional validation',
  'CHG-003': 'Update ReqBalEnq response elements',
  'CHG-004': 'Field value changes for ReqChkTxn',
}

/** Tab: By Change Request — accordion per CHG_ID with description; Download Excel = table format. */
function ByChangeRequestSection() {
  const [state, setState] = useState({})
  const [descriptions, setDescriptions] = useState({}) // { changeId: description }
  const [crById, setCrById] = useState({}) // { changeId: { changeType, ... } }
  const [loading, setLoading] = useState(true)
  const [isDummy, setIsDummy] = useState(false)
  const [expandedChgId, setExpandedChgId] = useState(null)
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const PAGE_SIZE = 20

  const normalizeAgentsForDisplay = (agentsMap) => {
    const map = agentsMap && typeof agentsMap === 'object' ? agentsMap : {}
    const entries = Object.entries(map).filter(([k]) => k)
    // Merge duplicates like Payer + Payer-agent by taking the highest-status.
    const rank = { RECEIVED: 1, APPLIED: 2, TESTED: 3, TESTS_READY: 4, READY: 5 }
    const bestByBase = new Map()
    const toBase = (name) => String(name || '').replace(/-agent$/i, '').trim()
    for (const [agent, status] of entries) {
      const base = toBase(agent)
      const s = String(status || '').toUpperCase() || 'RECEIVED'
      const prev = bestByBase.get(base)
      if (!prev || (rank[s] || 0) > (rank[prev.status] || 0)) {
        bestByBase.set(base, { base, status: s })
      }
    }
    return Array.from(bestByBase.entries())
      .map(([base, v]) => [base, v.status])
      .sort(([a], [b]) => String(a).localeCompare(String(b)))
  }

  const fetchStatus = async () => {
    setLoading(true)
    try {
      const [orchData, crRes] = await Promise.all([
        getOrchestratorStatus(),
        changeRequestAPI.getAllChangeRequests().catch(() => ({ data: [] })),
      ])
      const next = typeof orchData === 'object' && orchData !== null ? orchData : {}
      const hasRealData = Object.keys(next).length > 0
      setState(hasRealData ? next : DUMMY_ORCHESTRATOR_STATE)
      setIsDummy(!hasRealData)

      const list = Array.isArray(crRes?.data) ? crRes.data : []
      const descMap = {}
      const byId = {}
      list.forEach((cr) => {
        if (cr?.changeId) {
          descMap[cr.changeId] = cr.description || ''
          byId[cr.changeId] = { changeType: cr.changeType, description: cr.description }
        }
      })
      if (!hasRealData) {
        Object.assign(descMap, DUMMY_CHANGE_DESCRIPTIONS)
      }
      setDescriptions(descMap)
      setCrById(byId)
    } catch {
      setState(DUMMY_ORCHESTRATOR_STATE)
      setDescriptions(DUMMY_CHANGE_DESCRIPTIONS)
      setIsDummy(true)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
  }, [])

  const changeIds = Object.keys(state).sort()
  const hasRows = changeIds.length > 0

  const handleDownloadExcel = () => {
    exportByChangeRequest(state)
  }

  const q = String(query || '').trim().toLowerCase()
  const filteredChangeIds = changeIds.filter((cid) => {
    if (!q) return true
    const desc = String(descriptions[cid] || '').toLowerCase()
    return String(cid || '').toLowerCase().includes(q) || desc.includes(q)
  })
  const totalPages = Math.max(1, Math.ceil(filteredChangeIds.length / PAGE_SIZE))
  const safePage = Math.min(Math.max(1, page), totalPages)
  const pageChangeIds = filteredChangeIds.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE)

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wider">By Change Request</h3>
          <p className="text-xs text-slate-500 mt-1">Change requests with description and status. Expand to see status per bank/PSP.</p>
        </div>
        <div className="flex items-center gap-2">
          {isDummy && (
            <span className="text-xs text-amber-600 font-medium px-2 py-1 rounded bg-amber-50 border border-amber-200">Sample data</span>
          )}
          <Button variant="ghost" size="sm" onClick={fetchStatus} disabled={loading} className="text-slate-600">
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button variant="outline" size="sm" onClick={handleDownloadExcel} disabled={loading || !hasRows}>
            <Download className="mr-2 h-4 w-4" />
            Download Excel
          </Button>
        </div>
      </div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div className="flex-1 max-w-lg">
          <Input
            value={query}
            onChange={(e) => { setQuery(e.target.value); setPage(1) }}
            placeholder="Search by Change ID or description…"
            className="border-slate-200"
          />
        </div>
        <div className="text-xs text-slate-500">
          Showing {filteredChangeIds.length} change request(s)
        </div>
      </div>
      {loading ? (
        <p className="text-sm text-slate-500 py-6">Loading…</p>
      ) : !hasRows ? (
        <p className="text-sm text-slate-500 py-6">No party status reported yet.</p>
      ) : (
        <div className="border border-slate-200 rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="bg-slate-50/80 hover:bg-slate-50/80 border-b border-slate-200">
                <TableHead className="text-slate-600 font-medium w-[40px]"> </TableHead>
                <TableHead className="text-slate-600 font-medium">Change ID</TableHead>
                <TableHead className="text-slate-600 font-medium min-w-[200px]">Description</TableHead>
                <TableHead className="text-slate-600 font-medium w-[160px]">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {pageChangeIds.map((cid) => {
                const agentsMap = state[cid] || {}
                const displayEntries = normalizeAgentsForDisplay(agentsMap)
                const description = descriptions[cid] || '—'
                const isExpanded = expandedChgId === cid
                return (
                  <Fragment key={cid}>
                    {/* Collapsed: Change ID + Description only (no status) */}
                    <TableRow
                      className="bg-slate-50/60 hover:bg-slate-50 border-b border-slate-100 cursor-pointer"
                      onClick={() => setExpandedChgId(isExpanded ? null : cid)}
                    >
                      <TableCell className="py-3 align-middle w-[40px]">
                        <span className="text-slate-500 inline-flex">
                          {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                        </span>
                      </TableCell>
                      <TableCell className="py-3 align-middle">
                        <span className="font-mono font-semibold text-slate-900">{cid}</span>
                      </TableCell>
                      <TableCell className="py-3 align-middle">
                        <span className="text-sm text-slate-600 truncate block max-w-[400px]" title={description}>
                          {description}
                        </span>
                      </TableCell>
                      <TableCell className="py-3 align-middle" />
                    </TableRow>
                    {/* Expanded: Entity name + Status only (no description) */}
                    {isExpanded && (
                      displayEntries.length === 0 ? (
                        <TableRow className="bg-white hover:bg-slate-50/50">
                          <TableCell colSpan={4} className="py-2 pl-8 text-sm text-slate-500">
                            No bank/PSP status reported yet for this change request.
                          </TableCell>
                        </TableRow>
                      ) : (
                        displayEntries.map(([agent, status]) => {
                          const s = status || '—'
                          const rowPillClass = PARTY_STAGE_PILL_CLASS[s] || 'bg-slate-100 text-slate-700 border-0'
                          return (
                            <TableRow key={agent} className="bg-white hover:bg-slate-50/50 border-b border-slate-100 last:border-b-0">
                              <TableCell className="py-2 w-[40px]" />
                              <TableCell className="py-2 pl-8 align-middle font-medium text-slate-700">
                                {agent}
                              </TableCell>
                              <TableCell className="py-2 align-middle" />
                              <TableCell className="py-2 align-middle">
                                <span className={cn('inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium', rowPillClass)}>
                                  {String(s).replace(/_/g, ' ')}
                                </span>
                              </TableCell>
                            </TableRow>
                          )
                        })
                      )
                    )}
                  </Fragment>
                )
              })}
            </TableBody>
          </Table>
        </div>
      )}

      {!loading && filteredChangeIds.length > PAGE_SIZE && (
        <div className="flex items-center justify-between pt-2">
          <div className="text-xs text-slate-500">
            Page {safePage} of {totalPages}
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={safePage <= 1}>
              Prev
            </Button>
            <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={safePage >= totalPages}>
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

// ---- Orchestrator Status Report (construction-style dashboard) ----
const PIPELINE_STAGES = ['SENT', 'RECEIVED', 'APPLIED', 'TESTED', 'TESTS_READY', 'READY']
const STAGE_INDEX = Object.fromEntries(PIPELINE_STAGES.map((s, i) => [s, i]))
const STAGE_COLORS = {
  SENT: 'bg-slate-400',
  RECEIVED: 'bg-sky-400',
  APPLIED: 'bg-teal-500',
  TESTED: 'bg-amber-400',
  TESTS_READY: 'bg-amber-500',
  READY: 'bg-emerald-500',
}
const STAGE_LABELS = { SENT: 'Sent', RECEIVED: 'Received', APPLIED: 'Applied', TESTED: 'Tested', TESTS_READY: 'Tests Ready', READY: 'Ready' }

function getPipelineProgress(sent, orchestratorAgentsMap) {
  if (!orchestratorAgentsMap || typeof orchestratorAgentsMap !== 'object') {
    return { filledUpTo: sent ? 0 : -1, currentLabel: sent ? 'Sent' : '—', agents: [] }
  }
  const statuses = Object.values(orchestratorAgentsMap).filter(Boolean)
  let maxIdx = sent ? 0 : -1
  let bestStatus = null
  let bestRank = 0
  for (const s of statuses) {
    const idx = STAGE_INDEX[s] ?? -1
    if (idx > maxIdx) maxIdx = idx
    const rank = PARTY_STATUS_ORDER[s] ?? 0
    if (rank > bestRank) {
      bestRank = rank
      bestStatus = s
    }
  }
  const agents = Object.entries(orchestratorAgentsMap)
    .filter(([, v]) => v)
    .map(([agent, status]) => ({ agent, status }))
    .sort((a, b) => (PARTY_STATUS_ORDER[b.status] ?? 0) - (PARTY_STATUS_ORDER[a.status] ?? 0))
  return {
    filledUpTo: maxIdx,
    currentLabel: bestStatus ? STAGE_LABELS[bestStatus] ?? bestStatus : (sent ? 'Sent' : '—'),
    agents,
  }
}

function OrchestratorReportSection() {
  const [orchestratorStatus, setOrchestratorStatus] = useState({})
  const [deliveryStatus, setDeliveryStatus] = useState({}) // { partnerId: { changeId: { statusCode } } }
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [orchData, delivData] = await Promise.all([
        getOrchestratorStatus().catch(() => ({})),
        getManifestDeliveryStatus().catch(() => ({})),
      ])
      setOrchestratorStatus(typeof orchData === 'object' && orchData !== null ? orchData : {})
      setDeliveryStatus(typeof delivData === 'object' && delivData !== null ? delivData : {})
    } catch {
      setOrchestratorStatus({})
      setDeliveryStatus({})
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const changeIdsSet = new Set()
  Object.values(deliveryStatus).forEach((byChg) => {
    if (byChg && typeof byChg === 'object') Object.keys(byChg).forEach((cid) => changeIdsSet.add(cid))
  })
  Object.keys(orchestratorStatus).forEach((cid) => changeIdsSet.add(cid))
  const changeIds = Array.from(changeIdsSet).sort()

  const sentByChangeId = {}
  Object.entries(deliveryStatus).forEach(([partnerId, byChg]) => {
    if (!byChg || typeof byChg !== 'object') return
    Object.entries(byChg).forEach(([cid, result]) => {
      const code = result?.statusCode ?? result
      if (code === 200 || code === '200') sentByChangeId[cid] = true
    })
  })

  return (
    <div className="rounded-lg border border-gray-200 bg-white overflow-hidden shadow-sm">
      <div className="bg-amber-100 border-b border-amber-200 px-6 py-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-gray-900 tracking-tight">Orchestrator Status Report</h2>
            <p className="text-sm text-gray-700 mt-1">Manifest adoption by parties (Payer, Payee, Banks)</p>
          </div>
          <Button variant="outline" size="sm" onClick={fetchData} disabled={loading} className="border-amber-300 bg-white hover:bg-amber-50">
            <RefreshCw className={cn('mr-2 h-4 w-4', loading && 'animate-spin')} />
            Refresh
          </Button>
        </div>
      </div>

      <div className="px-6 py-3 bg-gray-50 border-b border-gray-200 flex flex-wrap items-center gap-4 text-xs">
        <span className="font-medium text-gray-600">Progress:</span>
        {PIPELINE_STAGES.map((stage) => (
          <span key={stage} className="flex items-center gap-1.5">
            <span className={cn('w-3 h-3 rounded-sm shrink-0', STAGE_COLORS[stage])} />
            <span className="text-gray-600">{STAGE_LABELS[stage]}</span>
          </span>
        ))}
      </div>

      <div className="p-6">
        {loading ? (
          <p className="text-sm text-gray-500 py-8">Loading…</p>
        ) : changeIds.length === 0 ? (
          <p className="text-sm text-gray-500 py-8">No change requests sent or reported yet. Publish a manifest to partners to see progress here.</p>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-b-2 border-gray-200 bg-gray-50/80">
                  <TableHead className="font-semibold text-gray-800 w-[120px]">Change ID</TableHead>
                  <TableHead className="font-semibold text-gray-800 min-w-[140px]">Partners / Agents</TableHead>
                  <TableHead className="font-semibold text-gray-800 min-w-[320px]">Progress</TableHead>
                  <TableHead className="font-semibold text-gray-800 w-[100px]">Current status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {changeIds.map((cid) => {
                  const sent = sentByChangeId[cid] === true
                  const agentsMap = orchestratorStatus[cid]
                  const { filledUpTo, currentLabel, agents } = getPipelineProgress(sent, agentsMap)
                  return (
                    <TableRow key={cid} className="border-b border-gray-100 hover:bg-gray-50/50">
                      <TableCell className="font-mono font-semibold text-gray-900 align-top pt-4">{cid}</TableCell>
                      <TableCell className="align-top pt-4">
                        {agents.length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {agents.map(({ agent, status }) => (
                              <Badge key={agent} variant={PARTY_STATUS_VARIANTS[status] || 'secondary'} className="text-xs capitalize">
                                {agent}: {status}
                              </Badge>
                            ))}
                          </div>
                        ) : (
                          <span className="text-gray-400 text-sm">—</span>
                        )}
                      </TableCell>
                      <TableCell className="align-top pt-3 pb-3">
                        <div className="flex rounded-md overflow-hidden border border-gray-200 shadow-inner bg-gray-100" style={{ minHeight: 28 }}>
                          {PIPELINE_STAGES.map((stage, i) => {
                            const filled = i <= filledUpTo || (i === 0 && sent)
                            return (
                              <div
                                key={stage}
                                className={cn(
                                  'flex-1 min-w-0 flex items-center justify-center py-1 px-0.5 text-[10px] font-medium text-white transition-colors',
                                  filled ? STAGE_COLORS[stage] : 'bg-gray-200 text-gray-400'
                                )}
                                title={STAGE_LABELS[stage]}
                              >
                                {filled && i === filledUpTo ? STAGE_LABELS[stage] : ''}
                              </div>
                            )
                          })}
                        </div>
                        <p className="text-xs text-gray-500 mt-1">Sent → Received → Applied → Tested → Tests Ready → Ready</p>
                      </TableCell>
                      <TableCell className="align-top pt-4">
                        <span className={cn(
                          'inline-block px-2 py-1 rounded text-sm font-medium',
                          currentLabel === 'Ready' && 'bg-emerald-100 text-emerald-800',
                          currentLabel === 'Tests Ready' && 'bg-amber-100 text-amber-800',
                          currentLabel === 'Tested' && 'bg-amber-50 text-amber-700',
                          currentLabel === 'Applied' && 'bg-teal-50 text-teal-800',
                          currentLabel === 'Received' && 'bg-sky-50 text-sky-800',
                          currentLabel === 'Sent' && 'bg-slate-100 text-slate-700',
                          (!currentLabel || currentLabel === '—') && 'bg-gray-100 text-gray-500'
                        )}>
                          {currentLabel}
                        </span>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </div>
  )
}

// partnerCrStatus: { [partnerId]: { [changeId]: { statusCode, response } } } — status per partner per CR
// orchestratorStatus: { [changeId]: { [agent]: status } } — party-reported status (RECEIVED/APPLIED/TESTED/READY)
function PublishManifestSection() {
  const [partners, setPartners] = useState({})
  const [partnerCrStatus, setPartnerCrStatus] = useState({}) // { partnerId: { changeId: { statusCode, response } } }
  const [orchestratorStatus, setOrchestratorStatus] = useState({}) // { changeId: { agent: status } }
  const [expandedBankId, setExpandedBankId] = useState(null)
  const [publishingPartner, setPublishingPartner] = useState(null)
  const [publishingCrId, setPublishingCrId] = useState(null)
  const [loadingPartners, setLoadingPartners] = useState(true)
  const [publishModalOpen, setPublishModalOpen] = useState(false)
  const [publishModalPartnerId, setPublishModalPartnerId] = useState(null)
  const [modalCrNumber, setModalCrNumber] = useState('')
  const [modalManifestFile, setModalManifestFile] = useState(null)
  const [modalDescription, setModalDescription] = useState('')
  const [modalSending, setModalSending] = useState(false)

  const refreshOrchestratorStatus = () => {
    getOrchestratorStatus()
      .then((data) => setOrchestratorStatus(typeof data === 'object' && data !== null ? data : {}))
      .catch(() => setOrchestratorStatus({}))
  }

  useEffect(() => {
    let cancelled = false
    listPartners()
      .then((data) => { if (!cancelled) setPartners(typeof data === 'object' && data !== null ? data : {}) })
      .catch(() => { if (!cancelled) setPartners({}) })
      .finally(() => { if (!cancelled) setLoadingPartners(false) })
    getManifestDeliveryStatus()
      .then((data) => {
        if (cancelled || typeof data !== 'object' || data === null || Array.isArray(data) || 'error' in data) return
        setPartnerCrStatus(data)
      })
      .catch(() => {})
    getOrchestratorStatus()
      .then((data) => {
        if (cancelled) return
        setOrchestratorStatus(typeof data === 'object' && data !== null ? data : {})
      })
      .catch(() => {})
    return () => { cancelled = true }
  }, [])

  const openPublishModal = (partnerId, crNumber = '') => {
    setPublishModalPartnerId(partnerId)
    setModalCrNumber(crNumber || '')
    setModalManifestFile(null)
    setModalDescription('')
    setPublishModalOpen(true)
  }

  const closePublishModal = () => {
    setPublishModalOpen(false)
    setPublishModalPartnerId(null)
    setModalSending(false)
    setPublishingCrId(null)
  }

  const handleModalSend = async (e) => {
    e.preventDefault()
    const id = (modalCrNumber || '').trim()
    if (!id) {
      alert('Enter CR number')
      return
    }
    if (!publishModalPartnerId) return
    setModalSending(true)
    setPublishingPartner(publishModalPartnerId)
    setPublishingCrId(id)
    try {
      if (modalManifestFile) {
        await uploadManifest(id, modalManifestFile)
      }
      const res = await sendManifestToPartner(id, publishModalPartnerId)
      setPartnerCrStatus((prev) => ({
        ...prev,
        [publishModalPartnerId]: {
          ...(prev[publishModalPartnerId] || {}),
          [id]: { statusCode: res?.data?.statusCode, response: res?.data?.response },
        },
      }))
      closePublishModal()
    } catch (err) {
      const msg = err?.response?.data?.detail ?? err?.response?.data?.error ?? err?.message ?? 'Send failed'
      setPartnerCrStatus((prev) => ({
        ...prev,
        [publishModalPartnerId]: {
          ...(prev[publishModalPartnerId] || {}),
          [id]: { statusCode: 'ERR', response: msg },
        },
      }))
      alert(`Send failed: ${msg}`)
    } finally {
      setModalSending(false)
      setPublishingPartner(null)
      setPublishingCrId(null)
    }
  }

  const handlePublishToPartner = (partnerId, crNumber = '') => {
    openPublishModal(partnerId, crNumber)
  }

  const getPartnerAgentKeys = (partnerId) => {
    const pid = String(partnerId || '').toUpperCase()
    const primary =
      pid === 'PAYER_AGENT' ? 'Payer'
      : pid === 'PAYEE_AGENT' ? 'Payee'
      : pid === 'REMITTER_AGENT' ? 'Remitter'
      : pid === 'BENEFICIARY_AGENT' ? 'Beneficiary'
      : partnerId

    const fallback =
      pid === 'PAYER_AGENT' ? 'Payer'
      : pid === 'PAYEE_AGENT' ? 'Payee'
      : pid === 'REMITTER_AGENT' ? 'Remitter'
      : pid === 'BENEFICIARY_AGENT' ? 'Beneficiary'
      : null

    return [primary, fallback].filter(Boolean)
  }

  const getPartnerPartyStatus = (partnerId, changeId) => {
    const agentsMap = orchestratorStatus?.[changeId]
    if (!agentsMap || typeof agentsMap !== 'object') return null
    const keys = getPartnerAgentKeys(partnerId)
    const rank = { RECEIVED: 1, APPLIED: 2, TESTED: 3, TESTS_READY: 4, READY: 5 }
    let best = null
    for (const k of keys) {
      const direct = agentsMap[k]
      const alt = agentsMap[`${k}-agent`]
      for (const s0 of [direct, alt]) {
        if (!s0) continue
        const s = String(s0).toUpperCase()
        if (!best || (rank[s] || 0) > (rank[best.status] || 0)) {
          best = { agent: k, status: s }
        }
      }
    }
    return best
  }

  const partnerEntries = Object.entries(partners)

  return (
    <div className="space-y-8">
      {/* Banks/PSPs — collapsible; table layout with nested CR rows */}
      <div className="rounded-lg border border-slate-200 bg-white p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wider">Bank / PSP</h3>
            <p className="text-xs text-slate-500 mt-1">Banks/PSPs with change requests and current stage. Publish per CR from the row action.</p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={refreshOrchestratorStatus} className="text-slate-600">
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh status
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => exportByPartner(partnerCrStatus, orchestratorStatus)}
              disabled={loadingPartners || Object.keys(partnerCrStatus).length === 0}
            >
              <Download className="mr-2 h-4 w-4" />
              Download Excel
            </Button>
          </div>
        </div>
        {loadingPartners ? (
          <p className="text-sm text-slate-500 py-6">Loading partners…</p>
        ) : partnerEntries.length === 0 ? (
          <p className="text-sm text-slate-500 py-6">No banks/PSPs configured (check partners.json).</p>
        ) : (
          <div className="border border-slate-200 rounded-lg overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="bg-slate-50/80 hover:bg-slate-50/80 border-b border-slate-200">
                  <TableHead className="text-slate-600 font-medium w-[40px]"> </TableHead>
                  <TableHead className="text-slate-600 font-medium">Bank / PSP</TableHead>
                  <TableHead className="text-slate-600 font-medium w-[200px]">Status</TableHead>
                  <TableHead className="text-slate-600 font-medium w-[140px] text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {partnerEntries.map(([partnerId, cfg]) => {
                  const crEntries = Object.entries(partnerCrStatus[partnerId] || {}).sort(([a], [b]) => (a || '').localeCompare(b || ''))
                  const isExpanded = expandedBankId === partnerId
                  return (
                    <Fragment key={partnerId}>
                      {/* Bank/PSP primary row — collapsible */}
                      <TableRow
                        className="bg-slate-50/60 hover:bg-slate-50 border-b border-slate-100 cursor-pointer"
                        onClick={() => setExpandedBankId((prev) => (prev === partnerId ? null : partnerId))}
                      >
                        <TableCell className="py-3 align-middle w-[40px]">
                          <span className="text-slate-500 inline-flex">
                            {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                          </span>
                        </TableCell>
                        <TableCell className="py-3 align-middle">
                          <div className="font-semibold text-slate-900">{partnerId}</div>
                        </TableCell>
                        <TableCell className="py-3 align-middle">
                          {crEntries.length > 0 ? (
                            <span className="text-xs text-slate-500">{crEntries.length} change request{crEntries.length !== 1 ? 's' : ''}</span>
                          ) : (
                            <span className="text-slate-400 text-xs">—</span>
                          )}
                        </TableCell>
                        <TableCell className="py-3 align-middle text-right" onClick={(e) => e.stopPropagation()}>
                          {/* No per-bank Publish button */}
                        </TableCell>
                      </TableRow>
                      {/* Nested CR rows — only when expanded */}
                      {isExpanded && (
                        crEntries.length === 0 ? (
                          <TableRow className="bg-white hover:bg-slate-50/50">
                            <TableCell colSpan={4} className="py-2 pl-8 text-sm text-slate-500">
                              No CRs sent to this bank/PSP yet. Publish from Change Management, then use the row &quot;Publish&quot; action per CR.
                            </TableCell>
                          </TableRow>
                        ) : (
                          crEntries.map(([crId, result]) => {
                          const code = result?.statusCode
                          const isSuccess = code === 200 || code === '200'
                          const ps = getPartnerPartyStatus(partnerId, crId)
                          const isPublishingThis = publishingPartner === partnerId && publishingCrId === crId
                          const pillClass = ps ? (PARTY_STAGE_PILL_CLASS[ps.status] || 'bg-slate-100 text-slate-700 border-0') : ''
                          return (
                            <TableRow key={crId} className="bg-white hover:bg-slate-50/50 border-b border-slate-100 last:border-b-0">
                              <TableCell className="py-2 w-[40px]" />
                              <TableCell className="py-2 pl-8 align-middle">
                                <span className="inline-flex items-center gap-2">
                                  {ps && (
                                    <span
                                      className="h-2 w-2 rounded-full shrink-0"
                                      style={{
                                        backgroundColor: ps.status === 'READY' ? 'rgb(16 185 129)' : ps.status === 'TESTS_READY' ? 'rgb(249 115 22)' : ps.status === 'TESTED' ? 'rgb(245 158 11)' : ps.status === 'APPLIED' ? 'rgb(59 130 246)' : 'rgb(100 116 139)',
                                      }}
                                      aria-hidden
                                    />
                                  )}
                                  <span className="font-mono text-sm text-slate-700">{crId}</span>
                                </span>
                              </TableCell>
                              <TableCell className="py-2 align-middle">
                                {!isSuccess ? (
                                  <span className="text-amber-600 text-sm" title={result?.response}>
                                    {code === 0 || code === '0' ? 'Error / Timeout' : (code ?? result?.response ?? '—')}
                                  </span>
                                ) : ps ? (
                                  <span className={cn('inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium', pillClass)}>
                                    {ps.status.replace(/_/g, ' ')}
                                  </span>
                                ) : (
                                  <span className="text-slate-400 text-xs">—</span>
                                )}
                              </TableCell>
                              <TableCell className="py-2 align-middle text-right">
                                <Button
                                  type="button"
                                  variant="ghost"
                                  size="sm"
                                  className="text-slate-600 hover:text-slate-900"
                                  onClick={(e) => { e.stopPropagation(); openPublishModal(partnerId, crId) }}
                                  disabled={isPublishingThis}
                                  title={`Publish ${crId} to this bank/PSP`}
                                >
                                  {isPublishingThis ? 'Sending…' : 'Publish'}
                                </Button>
                              </TableCell>
                            </TableRow>
                          )
                                })
                        )
                      )}
                    </Fragment>
                  )
                })}
              </TableBody>
            </Table>
          </div>
        )}
      </div>

      {/* Popup: Publish to partner — CR number, upload manifest, description, Send */}
      <Dialog open={publishModalOpen} onOpenChange={(open) => !open && closePublishModal()}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Publish changes to bank/PSP {publishModalPartnerId ?? ''}</DialogTitle>
            <DialogDescription>
              Enter CR number, upload manifest (optional), add description, then send.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleModalSend} className="space-y-4 mt-4">
            <div className="space-y-2">
              <Label htmlFor="modal-cr-number">CR number</Label>
              <Input
                id="modal-cr-number"
                placeholder="e.g. CHG-401"
                value={modalCrNumber}
                onChange={(e) => setModalCrNumber(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="modal-manifest-file">Upload manifest file</Label>
              <Input
                id="modal-manifest-file"
                type="file"
                accept=".json"
                onChange={(e) => setModalManifestFile(e.target.files?.[0] ?? null)}
                className="cursor-pointer"
              />
              {modalManifestFile && <p className="text-xs text-gray-500 truncate">{modalManifestFile.name}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="modal-description">Description</Label>
              <Textarea
                id="modal-description"
                placeholder="Describe the changes being published..."
                value={modalDescription}
                onChange={(e) => setModalDescription(e.target.value)}
                rows={3}
                className="resize-none"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="outline" onClick={closePublishModal} disabled={modalSending}>
                Cancel
              </Button>
              <Button type="submit" disabled={modalSending}>
                {modalSending ? 'Sending…' : 'Send'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}

function StatusCenterTab({ isActive, showClearAll = false }) {
  const toast = useToast()
  const [statusData, setStatusData] = useState([])
  const [loading, setLoading] = useState(false)
  const [clearing, setClearing] = useState(false)
  const [viewManifestOpen, setViewManifestOpen] = useState(false)
  const [viewManifestData, setViewManifestData] = useState(null)
  const [viewManifestChangeId, setViewManifestChangeId] = useState(null)
  const [manifestLoading, setManifestLoading] = useState(false)
  const [publishLoadingId, setPublishLoadingId] = useState(null)

  const handleViewManifest = async (changeId) => {
    setManifestLoading(true)
    setViewManifestChangeId(changeId)
    setViewManifestData(null)
    setViewManifestOpen(true)
    try {
      const data = await getManifest(changeId)
      if (data?.error === 'MANIFEST_NOT_FOUND') {
        toast.error('Manifest not found', 'Manifest may not be generated yet for this change request.')
        setViewManifestData(null)
      } else {
        setViewManifestData(data)
      }
    } catch (e) {
      toast.error('Failed to load manifest', e?.response?.data?.detail || e?.message || 'Please try again.')
      setViewManifestData(null)
    } finally {
      setManifestLoading(false)
    }
  }

  const handlePublishToAll = async (changeId) => {
    setPublishLoadingId(changeId)
    try {
      const res = await broadcastManifest(changeId)
      const data = res?.data ?? res
      if (data?.error === 'MANIFEST_NOT_FOUND') {
        toast.error('Cannot publish', 'Manifest not found. It may not be generated yet for this change request.')
        return
      }
      const report = data?.deliveryReport || {}
      const total = Object.keys(report).length
      const success = Object.values(report).filter((r) => r?.statusCode >= 200 && r?.statusCode < 300).length
      toast.success('Publish sent', `Sent to ${total} partner(s): ${success} succeeded.`)
      fetchStatus()
    } catch (e) {
      toast.error('Publish failed', e?.response?.data?.detail || e?.message || 'Please try again.')
    } finally {
      setPublishLoadingId(null)
    }
  }

  const fetchStatus = async () => {
    setLoading(true)
    try {
      const res = await changeRequestAPI.getAllChangeRequests()
      const list = Array.isArray(res.data) ? res.data : []
      setStatusData(list.map((r) => ({
        changeId: r.changeId,
        changeRequest: r.description,
        receivedDate: r.receivedDate,
        status: r.currentStatus,
        updatedOn: r.updatedOn,
        reviewComments: r.reviewComments,
      })))
    } catch (e) {
      console.error('Error fetching status:', e)
      setStatusData([])
    } finally {
      setLoading(false)
    }
  }

  const handleClearAll = async () => {
    if (!window.confirm('Clear all change requests from Change Management? This cannot be undone.')) return
    setClearing(true)
    try {
      await changeRequestAPI.clearAllChangeRequests()
      setStatusData([])
      toast.success('Cleared', 'All change requests have been removed.')
    } catch (e) {
      toast.error('Clear failed', e?.response?.data?.detail || e?.message || 'Please try again.')
    } finally {
      setClearing(false)
    }
  }

  useEffect(() => {
    if (isActive) fetchStatus()
  }, [isActive])

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Published':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />
      case 'Approved':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />
      case 'Deployed':
        return <CheckCircle2 className="h-5 w-5 text-emerald-500" />
      case 'Pending':
        return <Clock className="h-5 w-5 text-yellow-500" />
      case 'In Review':
      case 'Under Review':
        return <Clock className="h-5 w-5 text-purple-500" />
      case 'In Progress':
        return <Clock className="h-5 w-5 text-[#2F888A]" />
      case 'Failed':
      case 'Rejected':
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return <Clock className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'Published':
      case 'Approved':
        return 'bg-green-100 text-green-800'
      case 'Deployed':
        return 'bg-emerald-100 text-emerald-800'
      case 'Pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'In Review':
      case 'Under Review':
        return 'bg-purple-100 text-purple-800'
      case 'In Progress':
        return 'bg-[#2F888A]/15 text-[#2F888A]'
      case 'Failed':
      case 'Rejected':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <>
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Change Management</CardTitle>
            <CardDescription>Track change requests: submitted, with Developer, and approval status</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            {showClearAll && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearAll}
                disabled={clearing || statusData.length === 0}
                className="text-amber-700 border-amber-200 hover:bg-amber-50"
              >
                {clearing ? 'Clearing…' : 'Clear all'}
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={fetchStatus}
              disabled={loading}
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0 sm:p-6">
        <div className="w-full overflow-x-auto -mx-2 sm:mx-0">
        <Table className="w-full min-w-[720px]">
          <TableHeader>
            <TableRow>
              <TableHead className="w-[90px] min-w-[90px]">Change ID</TableHead>
              <TableHead className="w-[160px] min-w-[140px]">Description</TableHead>
              <TableHead className="w-[140px] min-w-[120px]">Submitted</TableHead>
              <TableHead className="w-[120px] min-w-[100px]">Status</TableHead>
              <TableHead className="w-[140px] min-w-[120px]">Updated On</TableHead>
              <TableHead className="w-[200px] min-w-[180px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {statusData.length === 0 && !loading ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-gray-500 py-8">
                  No change requests yet. Submit one from the Change Requests tab.
                </TableCell>
              </TableRow>
            ) : (
              statusData.map((row, index) => (
                <TableRow key={row.changeId || index}>
                  <TableCell className="font-medium text-sm whitespace-nowrap">{row.changeId}</TableCell>
                  <TableCell className="text-sm w-[160px] min-w-[140px] max-w-[160px] align-top overflow-hidden">
                    <span className="block text-wrap break-words line-clamp-2 whitespace-normal text-ellipsis overflow-hidden" title={row.changeRequest || ''}>{row.changeRequest || '-'}</span>
                  </TableCell>
                  <TableCell className="text-sm whitespace-nowrap" title={row.receivedDate || ''}>
                    {row.receivedDate ? new Date(row.receivedDate).toLocaleString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'Asia/Kolkata' }) : '-'}
                  </TableCell>
                  <TableCell className="text-sm overflow-hidden min-w-0 max-w-[140px]">
                    <div className="flex items-center gap-2 min-w-0 overflow-hidden">
                      <span className="shrink-0 flex-shrink-0">{getStatusIcon(row.status)}</span>
                      <span
                        className={`inline-block px-2 py-1 rounded-full text-xs font-medium truncate max-w-full ${getStatusColor(row.status)}`}
                        title={row.status || ''}
                      >
                        {row.status}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="text-sm whitespace-nowrap" title={row.updatedOn || ''}>
                    {row.updatedOn ? new Date(row.updatedOn).toLocaleString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false, timeZone: 'Asia/Kolkata' }) : '-'}
                  </TableCell>
                  <TableCell className="text-sm">
                    <div className="flex flex-wrap items-center gap-1.5 min-w-0">
                      {['approved', 'deployed'].includes(String(row.status || '').toLowerCase()) && (
                        <>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleViewManifest(row.changeId)}
                            disabled={manifestLoading}
                            className="text-slate-600 hover:text-slate-800 hover:bg-slate-50"
                            title="View manifest (generated after Developer approval)"
                          >
                            <ScrollText className="h-4 w-4 mr-1.5 inline" />
                            {manifestLoading && viewManifestChangeId === row.changeId ? '…' : 'View Manifest'}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handlePublishToAll(row.changeId)}
                            disabled={publishLoadingId != null}
                            className="text-green-600 hover:text-green-800 hover:bg-green-50"
                            title="Publish manifest to all banks/partners"
                          >
                            <Send className="h-4 w-4 mr-1.5 inline" />
                            {publishLoadingId === row.changeId ? '…' : 'Publish to ALL'}
                          </Button>
                        </>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
        </div>
      </CardContent>
    </Card>

    <Dialog open={viewManifestOpen} onOpenChange={setViewManifestOpen}>
      <DialogContent className="max-w-2xl max-h-[85vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Manifest {viewManifestChangeId ? `— ${viewManifestChangeId}` : ''}</DialogTitle>
          <DialogDescription>
            Manifest generated after Developer approval. Use &quot;Publish to ALL&quot; in Change Management to send to all partners.
          </DialogDescription>
        </DialogHeader>
        <div className="flex-1 min-h-0 overflow-auto rounded border bg-slate-50 p-3">
          {manifestLoading ? (
            <p className="text-sm text-gray-500">Loading…</p>
          ) : viewManifestData ? (
            <pre className="text-xs text-left whitespace-pre-wrap break-words font-mono">
              {JSON.stringify(viewManifestData, null, 2)}
            </pre>
          ) : (
            <p className="text-sm text-gray-500">No manifest data to display.</p>
          )}
        </div>
        <div className="flex justify-end pt-2">
          <Button variant="outline" onClick={() => setViewManifestOpen(false)}>Close</Button>
        </div>
      </DialogContent>
    </Dialog>
  </>
  )
}
