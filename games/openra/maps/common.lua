X = {}
X.Class_metatable = {}
-- Utility functions -----------------------------------------------------------
X.classConcat = function(l, r)
    local result = {}
    for k,v in pairs(l)
    do result[k] = v
    end
    for k,v in pairs(r)
    do result[k] = v
    end
    setmetatable(result, X.Class_metatable)
    return result
end
-- -----------------------------------------------------------------------------
X.classToString = function(cls)
    local result = "{"
    local first = true
    for k,v in cls
    do
        if first
        then first = false
        else result = result .. ", "
        end
        result = result .. tostring(k) .. "=" .. tostring(v)
    end
    return result .. "}"
end
-- Collection of all entities --------------------------------------------------
X.Class = {}
X.Class_metatable.__concat = X.classConcat
X.Class_metatable.__tostring = X.classToString
-- Activity types --------------------------------------------------------------
setmetatable(X.Class, X.Class_metatable)
-- Activity types --------------------------------------------------------------
X.ActivityType = {
    Interjection = X.Class..{},
    Complaint = X.Class..{}, 
    Poke = X.Class..{},
    Reaction = X.Class..{},
}
-- Activity --------------------------------------------------------------------
X.Activity = X.Class..{
    transcript = function(self)
        if self.expr
        then return self.expr
        end
        return "..."
    end
}
-- Actor -----------------------------------------------------------------------
X.Actor = X.Class..{
    name = "<unknown>",
    nameTag = function(self)
        return self.name
    end,
    act = function(self, ctxt)
    end,
    reactTo = function(self, ctxt)
    end
}
-- Initialize ------------------------------------------------------------------
X.initialize = function(self)
    for name, aType in pairs(self.ActivityType)
    do
        local aType = aType
        self.Activity["is"..name] = function(self)
            return self.activityType == aType
        end
        self[name] = self.Activity..{
            activityType = aType
        }
    end
end
-- Update ----------------------------------------------------------------------
X.update = function(self)
    for name,actor in pairs(self.actors)
    do actor:act(self);
    end
end
-- Print actor message ---------------------------------------------------------
X.actorMessage = function(self, actor, message)
    print("[" .. actor:nameTag() .. "]: " .. message)
end
-- Handle actor activity -------------------------------------------------------
X.handleActivity = function(self, source, activity)
    activity.source = source
    self:actorMessage(source, activity:transcript())
    for name,actor in pairs(self.actors)
    do
        if actor ~= source
        then actor:reactTo(activity, self)
        end
    end
end
-- -----------------------------------------------------------------------------
