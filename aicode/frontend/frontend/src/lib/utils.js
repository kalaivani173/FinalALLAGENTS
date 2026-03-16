import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

/**
 * Parse XSD text and return unique, sorted element names (xs:element with @name).
 * @param {string} xsdText - Raw XSD schema string
 * @returns {string[]}
 */
export function parseXsdElements(xsdText) {
  if (!xsdText || typeof xsdText !== 'string') return []
  try {
    const doc = new DOMParser().parseFromString(xsdText, 'text/xml')
    if (!doc?.documentElement) return []
    const all = doc.getElementsByTagName('*')
    const names = []
    for (let i = 0; i < all.length; i++) {
      const el = all[i]
      if (el.localName === 'element') {
        const n = el.getAttribute('name')
        if (n) names.push(n)
      }
    }
    return [...new Set(names)].sort()
  } catch {
    return []
  }
}

/**
 * Parse XSD and return:
 * - elements: unique element names (xs:element@name)
 * - attributesByElement: map of elementName -> unique attribute names found for that element
 *
 * This handles:
 * - inline complexType under an element
 * - element@type referencing a named complexType
 */
export function parseXsdElementsAndAttributes(xsdText) {
  if (!xsdText || typeof xsdText !== 'string') {
    return { elements: [], attributesByElement: {} }
  }
  try {
    // Some XSDs are UTF-16 and may get decoded into a string with NULs (\u0000).
    // Strip BOM and NULs to avoid false "invalid XSD" parsing.
    const cleaned = String(xsdText).replace(/^\uFEFF/, '').replace(/\u0000/g, '').trim()
    const parseWithMode = (mode) => {
      try {
        const d = new DOMParser().parseFromString(cleaned, mode)
        if (!d?.documentElement) return null
        return d
      } catch {
        return null
      }
    }

    // Some browsers/parsers behave differently for XSD; try both.
    const doc =
      parseWithMode('application/xml') ||
      parseWithMode('text/xml')

    if (!doc?.documentElement) return { elements: [], attributesByElement: {} }

    const all = doc.getElementsByTagName('*')
    // Detect XML parse errors (DOMParser returns a <parsererror/> document).
    // NOTE: Don't hard-bail immediately; some environments still include partial trees.
    let hasParserError = false
    for (let i = 0; i < all.length; i++) {
      if (all[i]?.localName === 'parsererror') {
        hasParserError = true
        break
      }
    }

    // Index complexTypes by name so element@type can resolve attributes.
    const complexTypesByName = new Map()
    const attributeGroupsByName = new Map()
    for (let i = 0; i < all.length; i++) {
      const node = all[i]
      if (node.localName === 'complexType') {
        const name = node.getAttribute('name')
        if (name) complexTypesByName.set(name, node)
      }
      if (node.localName === 'attributeGroup') {
        const name = node.getAttribute('name')
        if (name) attributeGroupsByName.set(name, node)
      }
    }

    const elements = new Set()
    const attributesByElement = {}

    const collectAttributesUnder = (rootNode, visitedCt = new Set(), visitedAg = new Set()) => {
      const attrs = []
      if (!rootNode) return attrs
      const subtree = rootNode.getElementsByTagName('*')
      for (let j = 0; j < subtree.length; j++) {
        const n = subtree[j]
        if (!n?.localName) continue
        if (n.localName === 'attribute') {
          // Only include attributes that belong to THIS complexType, not nested child elements.
          // Example: Payer complexType contains nested element Identity with its own attributes;
          // we don't want Identity attributes to show under Payer.
          let p = n.parentNode
          let nestedElementAncestor = false
          while (p && p !== rootNode) {
            if (p?.nodeType === 1 && p.localName === 'element') {
              nestedElementAncestor = true
              break
            }
            p = p.parentNode
          }
          if (nestedElementAncestor) continue

          const name = n.getAttribute('name')
          if (name) attrs.push(name)
        }
        // Follow attributeGroup refs
        if (n.localName === 'attributeGroup') {
          const ref = n.getAttribute('ref')
          if (ref) {
            const localRef = String(ref).split(':').pop()
            if (!visitedAg.has(localRef) && attributeGroupsByName.has(localRef)) {
              visitedAg.add(localRef)
              attrs.push(...collectAttributesUnder(attributeGroupsByName.get(localRef), visitedCt, visitedAg))
            }
          }
        }
        // Follow complexContent/simpleContent extension base types
        if (n.localName === 'extension') {
          const base = n.getAttribute('base')
          if (base) {
            const localBase = String(base).split(':').pop()
            if (!visitedCt.has(localBase) && complexTypesByName.has(localBase)) {
              visitedCt.add(localBase)
              attrs.push(...collectAttributesUnder(complexTypesByName.get(localBase), visitedCt, visitedAg))
            }
          }
        }
      }
      return attrs
    }

    for (let i = 0; i < all.length; i++) {
      const node = all[i]
      if (node.localName !== 'element') continue
      const elName = node.getAttribute('name')
      if (!elName) continue

      elements.add(elName)

      // Gather inline complexType attributes
      let attrs = []
      for (let c = 0; c < node.childNodes.length; c++) {
        const child = node.childNodes[c]
        if (child?.nodeType === 1 && child.localName === 'complexType') {
          attrs = attrs.concat(collectAttributesUnder(child))
        }
      }

      // Gather referenced complexType attributes (element@type)
      const typeRef = node.getAttribute('type')
      if (typeRef) {
        // Handle prefixes like tns:SomeType
        const localType = String(typeRef).split(':').pop()
        const ct = complexTypesByName.get(typeRef) || complexTypesByName.get(localType)
        if (ct) attrs = attrs.concat(collectAttributesUnder(ct))
      }

      const uniq = [...new Set(attrs)].sort()
      attributesByElement[elName] = uniq
    }

    const out = { elements: [...elements].sort(), attributesByElement }
    // If the parser reported an error but we still extracted elements, return them.
    // If we couldn't extract anything, treat it as invalid.
    if (hasParserError && out.elements.length === 0) {
      return { elements: [], attributesByElement: {} }
    }
    return out
  } catch {
    return { elements: [], attributesByElement: {} }
  }
}
