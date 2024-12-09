#include "RelationUtils.hpp"

#include "sc-agents-common/utils/IteratorUtils.hpp"

ScAddrVector RelationUtils::getNodeRoleRelationsByFilter(
    ScMemoryContext * m_context,
    ScAddr node,
    const std::function<bool(const ScAddr &)> & filter)
{
  ScAddrVector result;
  size_t i = 1;
  while (true)
  {
    ScAddr roleRelation = utils::IteratorUtils::getRoleRelation(m_context, i);
    ScAddr relNode = utils::IteratorUtils::getAnyByOutRelation(m_context, node, roleRelation);
    if (!relNode.IsValid())
    {
      break;
    }
    if (filter(relNode))
    {
      result.push_back(relNode);
    }
    ++i;
  }
  return result;
}