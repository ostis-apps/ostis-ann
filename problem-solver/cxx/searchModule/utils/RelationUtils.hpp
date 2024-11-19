#pragma once

#include <sc-memory/sc_agent.hpp>

class RelationUtils
{
public:
  static ScAddrVector getNodeRoleRelationsByFilter(
      ScMemoryContext * m_context,
      ScAddr node,
      const std::function<bool(const ScAddr &)>& filter);
};