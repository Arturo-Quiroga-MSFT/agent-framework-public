﻿// Copyright (c) Microsoft. All rights reserved.

using System;
using System.Collections.Frozen;
using System.Collections.Generic;

namespace Microsoft.Agents.AI.Workflows.Declarative.Kit;

/// <summary>
/// Describes an allowed declarative variable/type used in workflow configuration (primitives, lists, or record-like objects).
/// A record is modeled as IDictionary&lt;string, VariableType?&gt; along with an immutable schema for its fields.
/// </summary>
public sealed class VariableType
{
    // Canonical CLR type used to mark a "record" (object with named fields and per-field types).
    private static readonly Type s_typeRecord = typeof(IDictionary<string, VariableType?>);

    // All supported root CLR types (only these may appear directly as VariableType.Type).
    private static readonly FrozenSet<Type> s_supportedTypes =
        [
            typeof(bool),
            typeof(int),
            typeof(long),
            typeof(float),
            typeof(decimal),
            typeof(double),
            typeof(string),
            typeof(DateTime),
            typeof(TimeSpan),
            s_typeRecord,                 // Record (object with fields)
            typeof(IList<VariableType?>), // Homogeneous list of values (each element described by VariableType)
        ];

    /// <summary>
    /// Implicitly wraps a CLR <paramref name="type"/> as a <see cref="VariableType"/> (no validation is performed here).
    /// Use <see cref="IsValid()"/> or <see cref="IsValid(Type)"/> to confirm support.
    /// </summary>
    public static implicit operator VariableType(Type type) => new(type);

    /// <summary>
    /// Returns true if <typeparamref name="TValue"/> is a supported variable type.
    /// </summary>
    public static bool IsValid<TValue>() => IsValid(typeof(TValue));

    /// <summary>
    /// Returns true if the provided CLR <paramref name="type"/> is one of the supported root types.
    /// </summary>
    public static bool IsValid(Type type) => s_supportedTypes.Contains(type);

    /// <summary>
    /// Creates a record (object) variable type with the supplied <paramref name="fields"/> schema.
    /// Each tuple's Key is the field name; Type is the declared VariableType (nullable to allow "unknown"/late binding).
    /// </summary>
    public static VariableType Record(params IEnumerable<(string Key, VariableType? Type)> fields) =>
        new(typeof(IDictionary<string, VariableType?>))
        {
            Schema = fields.ToFrozenDictionary(kv => kv.Key, kv => kv.Type),
        };

    /// <summary>
    /// Initializes a new instance wrapping the given CLR <paramref name="type"/> (which should be one of the supported types).
    /// </summary>
    public VariableType(Type type)
    {
        this.Type = type;
    }

    /// <summary>
    /// The underlying CLR type that categorizes this variable (primitive, list, or record sentinel type).
    /// </summary>
    public Type Type { get; }

    /// <summary>
    /// Schema for record types: immutable mapping of field name to field VariableType (null means unspecified).
    /// Null for non-record VariableTypes.
    /// </summary>
    public FrozenDictionary<string, VariableType?>? Schema { get; init; }

    /// <summary>
    /// True if this instance represents a record/object with a field schema.
    /// </summary>
    public bool IsRecord => this.Type == s_typeRecord;

    /// <summary>
    /// Instance convenience wrapper for <see cref="IsValid(Type)"/> on this VariableType's underlying CLR type.
    /// </summary>
    public bool IsValid() => IsValid(this.Type);
}
