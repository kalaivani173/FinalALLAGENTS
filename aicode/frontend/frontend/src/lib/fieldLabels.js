/**
 * User-friendly field labels for UI forms
 * Maps technical field names to human-readable labels
 */

export const ArtifactsLabels = {
  existingXsd: {
    label: "Current XSD Schema",
    placeholder: "Upload current/existing XSD file",
    description: "The existing XSD schema file that defines the current structure"
  },
  proposedXsd: {
    label: "Proposed XSD Schema",
    placeholder: "Upload new/proposed XSD file",
    description: "The new XSD schema file with proposed changes"
  },
  sampleRequests: {
    label: "Sample Request Files",
    placeholder: "Upload sample request XML/JSON files",
    description: "Example request files showing the expected format"
  },
  sampleResponses: {
    label: "Sample Response Files",
    placeholder: "Upload sample response XML/JSON files",
    description: "Example response files showing the expected format"
  },
  brdDocuments: {
    label: "Business Requirements Documents",
    placeholder: "Upload BRD documents (PDF, DOCX)",
    description: "Business Requirements Document (BRD) and related specifications"
  }
}

export const ChangeItemLabels = {
  changeType: {
    label: "Type of Change",
    placeholder: "Select the type of change",
    description: "The category of change being requested",
    options: {
      ADD_FIELD: "Add New Field",
      MODIFY_ENUM: "Modify Enum Values",
      MODIFY_DATATYPE: "Modify Data Type",
      ADD_API: "Add New API"
    }
  },
  xmlPath: {
    label: "XML Element Path",
    placeholder: "e.g., ReqPay.Head.MsgId or ReqPay.Txn.Amount",
    description: "The XML path where the change should be applied"
  },
  oldType: {
    label: "Current Data Type",
    placeholder: "e.g., string, integer, decimal",
    description: "The existing data type of the field"
  },
  newType: {
    label: "New Data Type",
    placeholder: "e.g., string, integer, decimal",
    description: "The new data type for the field"
  },
  allowedValues: {
    label: "Allowed Values",
    placeholder: "Enter allowed values (comma-separated)",
    description: "List of valid values for enum or restricted fields"
  },
  mandatory: {
    label: "Field Requirement",
    placeholder: "Is this field mandatory?",
    description: "Whether this field is required or optional",
    options: {
      true: "Mandatory (Required)",
      false: "Optional"
    }
  },
  description: {
    label: "Change Description",
    placeholder: "Describe the change in detail...",
    description: "Detailed description of what needs to be changed"
  }
}

export const ChangeRequestLabels = {
  changeId: {
    label: "Change Request ID",
    placeholder: "Auto-generated or enter manually",
    description: "Unique identifier for this change request"
  },
  changeCategory: {
    label: "Change Category",
    placeholder: "Select category",
    description: "Whether this is for an existing API or a new API",
    options: {
      EXISTING_API: "Existing API Modification",
      NEW_API: "New API Addition"
    }
  },
  apiName: {
    label: "API Name",
    placeholder: "e.g., ReqPay, ReqRegMob, ReqOtp",
    description: "Name of the API being modified or created"
  },
  apiVersion: {
    label: "API Version",
    placeholder: "e.g., 1.0, 2.0, 2.1",
    description: "Version number of the API"
  },
  description: {
    label: "Change Request Description",
    placeholder: "Provide a comprehensive description of the change request...",
    description: "Overall description of what this change request aims to achieve"
  },
  artifacts: {
    label: "Supporting Documents",
    placeholder: "Upload supporting files",
    description: "XSD schemas, sample files, and documentation"
  },
  changeItems: {
    label: "Change Specifications",
    placeholder: "Add change items",
    description: "Detailed list of individual changes to be made"
  }
}

// Helper function to get label for a field
export function getFieldLabel(model, fieldName) {
  const labels = {
    Artifacts: ArtifactsLabels,
    ChangeItem: ChangeItemLabels,
    ChangeRequest: ChangeRequestLabels
  }
  
  return labels[model]?.[fieldName]?.label || fieldName
}

// Helper function to get full field info
export function getFieldInfo(model, fieldName) {
  const labels = {
    Artifacts: ArtifactsLabels,
    ChangeItem: ChangeItemLabels,
    ChangeRequest: ChangeRequestLabels
  }
  
  return labels[model]?.[fieldName] || { label: fieldName }
}
